from mininet.topo import Topo

class FatTreeTopo(Topo):
    def build(self):
        core_s = []
        aggr_s = []
        edge_s = []
        hosts = []

        # c0,c1,c2,c3,dpid末尾为1,核心交换机
        for i in range(4):
            sw = self.addSwitch(f'c{i}',dpid=f'00000000000000{i}1')
            core_s.append(sw)
        
        for pod in range(4):
            # a00,a01,a10,a11,a20,a21,a30,a31,聚合交换机
            pod_aggr_s = []
            for i in range(2):
                sw = self.addSwitch(f'a{pod}{i}',dpid=f'0000000000000{pod}{i}2')
                pod_aggr_s.append(sw)
            aggr_s.append(pod_aggr_s)

            pod_edge_s = []
            # e00,e01,e10,e11,e20,e21,e30,e31,聚合交换机
            for i in range(2):
                sw = self.addSwitch(f'e{pod}{i}',dpid=f'0000000000000{pod}{i}3')
                pod_edge_s.append(sw)
            edge_s.append(pod_edge_s)
 
            #连接汇聚交换机和核心交换机
            for edge_sw in pod_edge_s:
                for aggr_sw in pod_aggr_s:
                    self.addLink(aggr_sw,edge_sw)

            # h000 h001 h010 h011 ... h300 h301 h310 h311
            for i in range(2):
                for j in range(2):
                    ht= self.addHost(f'h{pod}{i}{j}')
                    self.addLink(ht,pod_edge_s[i])
                    hosts.append(ht)
        
        for i in range(4):
            for j in range(2):
                if( j == 0):
                    for k in range (0,2):
                        self.addLink(aggr_s[i][j],core_s[k])
                if( j == 1):
                    for k in range (2,4):
                        self.addLink(aggr_s[i][j],core_s[k])


topos = {'mytopo': FatTreeTopo}