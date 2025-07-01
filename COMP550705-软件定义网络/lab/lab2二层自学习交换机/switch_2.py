from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from os_ken.controller.handler import set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet
from os_ken.lib.packet import ethernet
from os_ken.lib.packet import arp
from os_ken.lib.packet import ether_types

# 定义常量
ETHERNET = ethernet.ethernet.__name__
ETHERNET_MULTICAST = "ff:ff:ff:ff:ff:ff"
ARP = arp.arp.__name__

class Switch_Dict(app_manager.OSKenApp):
    """支持环路防护的自学习交换机"""
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Switch_Dict, self).__init__(*args, **kwargs)
        self.mac_to_port = {}  # MAC地址学习表: dpid -> {mac: port}
        self.arp_map = {}  # ARP请求记录表: (dpid, src_mac, dst_ip) -> in_port

    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, hard_timeout=0):
        """下发流表项到交换机"""
        dp = datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        
        # 构造流表项指令
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        
        # 创建FlowMod消息
        mod = parser.OFPFlowMod(
            datapath=dp,
            priority=priority,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout,
            match=match,
            instructions=inst
        )
        
        # 发送流表项
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """处理交换机连接事件"""
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        
        # 添加默认流表项（table-miss）
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        self.add_flow(dp, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """处理Packet-In消息"""
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        
        # 获取交换机ID和入端口
        dpid = dp.id
        in_port = msg.match['in_port']
        
        # 解析数据包
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)

        # 过滤LLDP和IPv6数据包
        if eth_pkt.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        if eth_pkt.ethertype == ether_types.ETH_TYPE_IPV6:
            return

        # 获取源/目的MAC地址
        dst = eth_pkt.dst
        src = eth_pkt.src

        drop_packet = False

        header_list = dict((p.protocol_name, p) for p in pkt.protocols if type(p) != str)
        if dst == ETHERNET_MULTICAST and ARP in header_list:
            arp_pkt = pkt.get_protocol(arp.arp) 
            dst_ip = arp_pkt.dst_ip
            arp_key = (dpid,src,dst_ip)
            if arp_key in self.arp_map:
                if self.arp_map[arp_key] != in_port:
                    drop_packet = True
            self.arp_map[arp_key] = in_port
        
        if not drop_packet:
            self.mac_to_port.setdefault(dpid,{})
            self.mac_to_port[dpid][src] = in_port

            if dst in self.mac_to_port[dpid]:
                actions = [parser.OFPActionOutput(self.mac_to_port[dpid][dst])]
                match = parser.OFPMatch(eth_dst = dst)
                self.add_flow(dp,1,match,actions,idle_timeout=20)
            else:
                actions = [parser.OFPActionOutput(ofp.OFPP_FLOOD)]

            data = None
            if msg.buffer_id == ofp.OFP_NO_BUFFER:
                data = msg.data

            out = parser.OFPPacketOut(
                datapath = dp,
                buffer_id = msg.buffer_id,
                in_port = in_port,
                actions = actions,
                data=data
            )
            dp.send_msg(out)
        else:
            out = parser.OFPPacketOut(
                datapath=dp,
                buffer_id=msg.buffer_id,
                in_port=in_port,
                actions=[],
                data=None
            )
            dp.send_msg(out)
        
        