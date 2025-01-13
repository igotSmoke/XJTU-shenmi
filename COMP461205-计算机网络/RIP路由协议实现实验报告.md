# 实验二 RIP路由协议软件实验

### 实验目的

    本实验旨在通过软件实现RIP（路由信息协议），深入分析和理解距离矢量路由算法的工作原理，从而掌握网络协议的构建流程。

### 实验内容

    1.实现路由器的核心功能：这包括建立、更新和维护路由表，以及基于这些路由表管理数据包的转发过程。
    2.设计网络拓扑图：需要设计一个组网图，并为不同的网络路径分配不同的权重。
    3.确保程序的稳定性和效率：使程序能够快速响应网络中的突发情况，同时保证代码的鲁棒性。
   
### 分工情况
    该实验由组员X[学号：XX]完成。

### 实验简述

#### Stage1:Static Routes
    该阶段实现向路由表中添加静态路由，即不会过期的主机与路由器相连的路由信息。
#### Stage2:Forwarding
    在阶段一之后，连接到同一个路由器的主机并不能相互ping通，因此需要实现路由器的转发逻辑。
    若路由表中存有目的主机的可达表项，则转发。
#### Stage3:Sending Routing Tables Advertisements
    在阶段二之后，连接到不同的相连的路由器的主机并不能相互ping通，需要实现路由器对路由信息的转发。
#### Stage4:Handle Route Advertisements
    在阶段三之后，路由器需要对收到的路由信息进行处理。
    若路由表中没有目的主机表项，则将新路由信息加入到路由表中。
    若路由表中已存在目的主机表项，若端口相同，则更新；
    若端口不同，则比较延迟，若延迟更低，则更新。
#### Stage5:Handling Routing Tables Timeouts
    在阶段四之后，若删除某两个路由器的连接，转发可能会出错，因为过期路由没有得到处理。
    因此路由器需要对过期路由进行处理。若路由过期，则删除。

至此，RIP路由协议的基本功能全部实现。

### 实验结果
    运行h1.ping(h4),包走的是最短路径(a->b->c->d)，且没有出现泄洪现象。测试程序跑出50分。

### 源代码
``````
dv_router.cpp
import sim.api as api
from cs168.dv import RoutePacket, \
                     Table, TableEntry, \
                     DVRouterBase, Ports, \
                     FOREVER, INFINITY

class DVRouter(DVRouterBase):

    # A route should time out after this interval
    ROUTE_TTL = 15

    # Dead entries should time out after this interval
    GARBAGE_TTL = 10

    # -----------------------------------------------
    # At most one of these should ever be on at once
    SPLIT_HORIZON = False
    POISON_REVERSE = False
    # -----------------------------------------------
    
    # Determines if you send poison for expired routes
    POISON_EXPIRED = False

    # Determines if you send updates when a link comes up
    SEND_ON_LINK_UP = False

    # Determines if you send poison when a link goes down
    POISON_ON_LINK_DOWN = False

    def __init__(self):
        """
        Called when the instance is initialized.
        DO NOT remove any existing code from this method.
        However, feel free to add to it for memory purposes in the final stage!
        """
        assert not (self.SPLIT_HORIZON and self.POISON_REVERSE), \
                    "Split horizon and poison reverse can't both be on"
        
        self.start_timer()  # Starts signaling the timer at correct rate.

        # Contains all current ports and their latencies.
        # See the write-up for documentation.
        self.ports = Ports()
        
        # This is the table that contains all current routes
        self.table = Table()
        self.table.owner = self

    

    def add_static_route(self, host, port):
        """
        Adds a static route to this router's table.

        Called automatically by the framework whenever a host is connected
        to this router.

        :param host: the host.
        :param port: the port that the host is attached to.
        :returns: nothing.


        """
        # `port` should have been added to `peer_tables` by `handle_link_up`
        # when the link came up.
        assert port in self.ports.get_all_ports(), "Link should be up, but is not."

        # TODO: fill this in!
        host_latency = self.ports.get_latency(port)

        entry = TableEntry(host,port,host_latency,FOREVER)

        self.table[host] = entry

    def handle_data_packet(self, packet, in_port):
        """
        Called when a data packet arrives at this router.

        You may want to forward the packet, drop the packet, etc. here.

        :param packet: the packet that arrived.
        :param in_port: the port from which the packet arrived.
        :return: nothing.

        """
        packet_dst = packet.dst
        if packet_dst in self.table:
            packet_dst_entry = self.table[packet_dst]

            if packet_dst_entry.latency >= INFINITY:
                self.s_log("Dropping packet to %s, beacuse the latency is INFINITY.", packet_dst)
                
            else:
                send_port = packet_dst_entry.port

                if send_port != in_port:
                    self.send(packet, send_port)
                else:
                    self.s_log("Dropping packet to %s, beacuse the port to be sent is the port who send the packet.", packet_dst)

        else:
            self.s_log("Dropping packet, No route to %s", packet_dst)


    def send_routes(self, force=False, single_port=None):
        """
        Send route advertisements for all routes in the table.

        :param force: if True, advertises ALL routes in the table;
                      otherwise, advertises only those routes that have
                      changed since the last advertisement.
               single_port: if not None, sends updates only to that port; to
                            be used in conjunction with handle_link_up.
        :return: nothing.

        """
        # TODO: fill this in!

        if force:
            for dst,entry in self.table.items():
                route_packet = RoutePacket(destination = dst,latency=entry.latency)

                for port in self.ports.get_all_ports():
                    self.send(route_packet, port)
        
    def expire_routes(self):
        """
        Clears out expired routes from table.
        accordingly.
        """
        # TODO: fill this in!
        expired_routes = []

        for route_dst, entry in self.table.items():
            if entry.expire_time <= api.current_time():
                expired_routes.append(route_dst)
        
        for route_dst in expired_routes:
            del self.table[route_dst]
            self.s_log(f"Route to {route_dst} expired.")


    def handle_route_advertisement(self, route_dst, route_latency, port):
        """
        Called when the router receives a route advertisement from a neighbor.

        :param route_dst: the destination of the advertised route.
        :param route_latency: latency from the neighbor to the destination.
        :param port: the port that the advertisement arrived on.
        :return: nothing.

        """
        # TODO: fill this in!

        if route_latency == INFINITY: 
            if route_dst in self.table and self.table[route_dst].port == port:
                entry = self.table[route_dst]
                if (entry.latency < INFINITY): 
                    new_expire_time=self.ROUTE_TTL + api.current_time()
                else:
                    new_expire_time=entry.expire_time
                self.table[route_dst] = TableEntry(
                    dst = route_dst, 
                    port=port, 
                    latency=INFINITY,
                    expire_time= new_expire_time
                    )        
        else:
            exist_entry = self.table.get(route_dst)

            port_latency = self.ports.get_latency(port)
            new_latency = port_latency + route_latency

            if exist_entry is None:
                self.table[route_dst] = TableEntry(route_dst, port, new_latency, api.current_time() + self.ROUTE_TTL)
            else:
                if self.table[route_dst].port == port or new_latency < exist_entry.latency:
                    self.table[route_dst] = TableEntry(route_dst, port, new_latency, api.current_time() + self.ROUTE_TTL)


    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this router goes up.

        :param port: the port that the link is attached to.
        :param latency: the link latency.
        :returns: nothing.
        """
        self.ports.add_port(port, latency)

        # TODO: fill in the rest!

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this router does down.

        :param port: the port number used by the link.
        :returns: nothing.
        """
        self.ports.remove_port(port)

        # TODO: fill this in!

    # Feel free to add any helper methods!

``````

``````
myTopo.py
import sim

def launch (switch_type = sim.config.default_switch_type, host_type = sim.config.default_host_type):
  """
  Creates a topology with loops.

  It looks like:

           h2
           |
           sB
          /|\
  h1 -- sA | sD -- h4
          \|/
           sC
           |
           h3

  """
  switch_type.create('sA')
  switch_type.create('sB')
  switch_type.create('sC')
  switch_type.create('sD')

  host_type.create('h1')
  host_type.create('h2')
  host_type.create('h3')
  host_type.create('h4')

  sA.linkTo(sB, latency=2)
  sA.linkTo(sC, latency=7)
  sB.linkTo(sC, latency=1)
  sB.linkTo(sD, latency=3)
  sC.linkTo(sD, latency=1)

  sA.linkTo(h1, latency=1)
  sB.linkTo(h2, latency=1)
  sC.linkTo(h3, latency=1)
  sD.linkTo(h4, latency=1)
``````

### 实验总结
成功通过软件实现RIP（路由信息协议），深入分析和理解了距离矢量路由算法的工作原理，从而掌握了网络协议的构建流程。