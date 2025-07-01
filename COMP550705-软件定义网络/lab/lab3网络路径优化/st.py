# os_ken-manager shortest_forward.py --observe-links
from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER, HANDSHAKE_DISPATCHER
from os_ken.controller.handler import set_ev_cls
from os_ken.controller.handler import set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet
from os_ken.lib.packet import ethernet, arp, ipv4
from os_ken.controller import ofp_event
from os_ken.topology import event
from os_ken.base.app_manager import lookup_service_brick
import sys
from network_awareness import NetworkAwareness
from os_ken.topology.switches import LLDPPacket
import networkx as nx
from os_ken.topology.api import get_switch
ETHERNET = ethernet.ethernet.__name__
ETHERNET_MULTICAST = "ff:ff:ff:ff:ff:ff"
ARP = arp.arp.__name__
ETH_TYPE_IPV4 = 0x0800
ETH_TYPE_ARP = 0X0806

class ShortestForward(app_manager.OSKenApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {
        'network_awareness': NetworkAwareness
    }

    def __init__(self, *args, **kwargs):
        super(ShortestForward, self).__init__(*args, **kwargs)
        self.network_awareness = kwargs['network_awareness']
        self.weight = 'delay'
        self.mac_to_port = {}
        self.sw = {}
        self.path=None

    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, hard_timeout=0):
        dp = datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=dp, priority=priority,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout,
            match=match, instructions=inst)
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        dpid = dp.id
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)

        pkt_type = eth_pkt.ethertype

        # layer 2 self-learning
        dst_mac = eth_pkt.dst
        src_mac = eth_pkt.src

        if isinstance(arp_pkt, arp.arp):
            self.handle_arp(msg, in_port, dst_mac, src_mac, pkt, pkt_type)

        if isinstance(ipv4_pkt, ipv4.ipv4):
            self.handle_ipv4(msg, ipv4_pkt.src, ipv4_pkt.dst, pkt_type)

    def handle_arp(self, msg, in_port, dst, src, pkt, pkt_type):
        #just handle loop here
        #just like your code in exp1 mission2
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        dpid = dp.id
        self.mac_to_port.setdefault(dpid, {})

        drop = False
        header_list = dict((p.protocol_name, p) for p in pkt.protocols if type(p) != str)
        if dst == ETHERNET_MULTICAST and ARP in header_list:
            dst_ip = header_list[ARP].dst_ip
            arp_key = (dpid,src,dst_ip)
            if arp_key in self.sw:
                if self.sw[arp_key] != in_port:
                    drop = True
            else:
                self.sw[arp_key] = in_port
        
        if drop:
            out = parser.OFPPacketOut(
                datapath=dp, 
                buffer_id=msg.buffer_id,
                in_port=in_port, 
                actions=[], 
                data=None)
            dp.send_msg(out)
        else:
            self.mac_to_port[dpid][src] = in_port

            if dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
            else:
                out_port = ofp.OFPP_FLOOD

            actions = [parser.OFPActionOutput(out_port)]

            if out_port != ofp.OFPP_FLOOD:
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_type=pkt_type)
                self.add_flow(dp, 1, match, actions, hard_timeout=5)
        
            data = None
            if msg.buffer_id == ofp.OFP_NO_BUFFER:
                data = msg.data
        
            out = parser.OFPPacketOut(
                datapath=dp, 
                buffer_id=msg.buffer_id,
                in_port=in_port, 
                actions=actions, 
                data=data)
            dp.send_msg(out)

    def handle_ipv4(self, msg, src_ip, dst_ip, pkt_type):
        parser = msg.datapath.ofproto_parser

        dpid_path = self.network_awareness.shortest_path(src_ip, dst_ip, weight=self.weight)
        if not dpid_path:
            return

        self.path=dpid_path
        # get port path:  h1 -> in_port, s1, out_port -> h2
        port_path = []
        for i in range(1, len(dpid_path) - 1):
            in_port = self.network_awareness.link_info[(dpid_path[i], dpid_path[i - 1])]
            out_port = self.network_awareness.link_info[(dpid_path[i], dpid_path[i + 1])]
            port_path.append((in_port, dpid_path[i], out_port))
        self.show_path(src_ip, dst_ip, port_path)

        # calc path delay


        # send flow mod
        for node in port_path:
            in_port, dpid, out_port = node
            self.send_flow_mod(parser, dpid, pkt_type, src_ip, dst_ip, in_port, out_port)
            self.send_flow_mod(parser, dpid, pkt_type, dst_ip, src_ip, out_port, in_port)

        # send packet_out
        _, dpid, out_port = port_path[-1]
        dp = self.network_awareness.switch_info[dpid]
        actions = [parser.OFPActionOutput(out_port)]
        out = parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=msg.data)
        dp.send_msg(out)

    def send_flow_mod(self, parser, dpid, pkt_type, src_ip, dst_ip, in_port, out_port):
        dp = self.network_awareness.switch_info[dpid]
        match = parser.OFPMatch(
            in_port=in_port, eth_type=pkt_type, ipv4_src=src_ip, ipv4_dst=dst_ip)
        actions = [parser.OFPActionOutput(out_port)]
        self.add_flow(dp, 1, match, actions, 10, 30)

    def show_path(self, src, dst, port_path):
        self.logger.info('path: {} -> {}'.format(src, dst))
        path = src + ' -> '
        for node in port_path:
            path += '{}:s{}:{}'.format(*node) + ' -> '
        path += dst
        self.logger.info(path)

    def delete_flow(self, datapath, match):
        dp = datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        mod = parser.OFPFlowMod(
                datapath=dp, 
                command=ofp.OFPFC_DELETE,
                out_port=ofp.OFPP_ANY, 
                out_group=ofp.OFPG_ANY,
                priority=1, 
                match=match)
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def fault_tolerant_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        parser = dp.ofproto_parser

        for switch in get_switch(self):
            datapath = switch.dp
            match_ipv4 = parser.OFPMatch(eth_type = ETH_TYPE_IPV4)
            match_arp = parser.OFPMatch(eth_type = ETH_TYPE_ARP)
            self.delete_flow(datapath, match_ipv4)
            self.delete_flow(datapath, match_arp)            


        self.mac_to_port.clear()
        self.sw.clear()
        self.network_awareness.topo_map.clear()