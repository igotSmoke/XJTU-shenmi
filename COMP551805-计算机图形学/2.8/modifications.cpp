optional<Edge*> HalfedgeMesh::flip_edge(Edge* e)
{
    if (e->on_boundary())//在边界上
    {
        return std::nullopt;
    }
    else
    {        
        
        Halfedge* h12 = e->halfedge;
        Halfedge* h21 = h12->inv;
        Halfedge* h23 = h12->next;
        Halfedge* h31 = h23->next;
        Halfedge* h14 = h21->next;
        Halfedge* h42 = h14->next;

        Vertex* v4 = h42->from;
        Vertex* v3 = h31->from;

        //修改h12的连接关系
        h12->next = h31;
        h12->prev = h14;
        h12->from = v4;
        h12->face = h31->face;
        // 修改h21的连接关系
        h21->next = h42;
        h21->prev = h23;
        h21->from = v3;
        h21->face = h42->face;
        //修改h31，h14,h42,h23的连接关系
        h31->prev = h12;
        h31->next = h14;
        
        h14->next = h12;
        h14->prev = h31;
        h14->face = h12->face;

        h42->next = h23;
        h42->prev = h21;
        
        h23->next = h21;
        h23->prev = h42;
        h23->face = h21->face;
        
        //修改面，顶点的halfedge
        h21->face->halfedge = h21;
        h12->face->halfedge = h12;

        v3->halfedge = h21;
        v4->halfedge = h12;

        return e;
    }
    
}

optional<Vertex*> HalfedgeMesh::split_edge(Edge* e)
{
    if (e->on_boundary()) // 在边界上
    {
        Halfedge* h12 = e->halfedge;
        if (!h12->is_boundary())
            h12 = h12->inv;

        Face* f_ver = h12->face;


        Halfedge* h21 = h12->inv;
        Halfedge* h14 = h21->next;
        Halfedge* h42 = h14->next;

        Vertex* v4 = h42->from;
        Vertex* v1 = h12->from;
        Vertex* v2 = h21->from;

        Halfedge* h[6];
        h[0] = h12;
        h[4] = h21;
        for (int i = 0; i < 6; ++i)
            if (i != 0 && i != 4)
                h[i] = new_halfedge();
        
        Vertex* v_new = new_vertex();
        Edge* e_new[3];

        e_new[0] = e;
        for (int i = 1; i < 3; ++i) e_new[i] = new_edge();

        Face* f_new[3];
        f_new[0] = f_ver;
        f_new[1] = h14->face;
        f_new[2] = new_face();

        //半边关系重建
        h42->face = f_new[2];
        h14->prev = h[1];
        h14->next = h[2];
        h42->prev = h[3];
        h42->next = h[4];

        Halfedge* h_right = h[0]->next;//还未重设
        Halfedge* h_left  = h[0]->prev;//还未重设

        //(Halfedge *next, Halfedge *prev, Halfedge *inv, Vertex *from, Edge *edge, Face *face)
        h[0]->set_neighbors(h[5], h_left, h[1], v1, e_new[0], f_new[0]);
        h[1]->set_neighbors(h14, h[2], h[0], v_new, e_new[0], f_new[1]);
        h[2]->set_neighbors(h[1], h14, h[3], v4, e_new[1], f_new[1]);
        h[3]->set_neighbors(h42, h[4], h[2], v_new, e_new[1], f_new[2]);
        h[4]->set_neighbors(h[3], h42, h[5], v2, e_new[2], f_new[2]);
        h[5]->set_neighbors(h_right, h[0], h[4], v_new, e_new[2], f_new[0]);

        h_right->prev = h[5];

        // 顶点关系重建
        v1->halfedge = h[0];
        v2->halfedge = h[4];
        v4->halfedge = h[2];

        v_new->halfedge = h[1];
        v_new->pos      = (v1->pos + v2->pos) / 2;
        v_new->is_new   = true;

        // 边关系重建
        for (int i = 0; i < 3; ++i) e_new[i]->halfedge = h[2 * i];
        e_new[1]->is_new = true; 

        // 面关系重建
        for (int i = 0; i < 3; ++i) f_new[i]->halfedge = h[2 * i];
        validate();
        return v_new;

    } else {
        // 需要新建六个半边，一个顶点，三条边，两个面
        Halfedge* h12 = e->halfedge;
        Halfedge* h21 = h12->inv;
        Halfedge* h23 = h12->next;
        Halfedge* h31 = h23->next;
        Halfedge* h14 = h21->next;
        Halfedge* h42 = h14->next;

        Vertex* v4 = h42->from;
        Vertex* v3 = h31->from;
        Vertex* v2 = h21->from;
        Vertex* v1 = h12->from;

        // 半边新建
        Halfedge* h[8]; // h12(h1n),hn1 h4n hn4 h2n(h21) hn2 h3n hn3
        h[0] = h12;
        h[4] = h21;
        for (int i = 0; i < 8; ++i)
            if (i!=0 && i!=4)
                h[i] = new_halfedge();

        // 顶点和edge新建
        Vertex* v_new = new_vertex();
        Edge* e_new[4]; // 1n,2n,3n,4n
        
        e_new[0] = e;
        for (int i = 1; i < 4; ++i) e_new[i] = new_edge();
        
        // 面新建
        Face* f_new[4];
        f_new[0] = h31->face;
        f_new[1] = new_face();
        f_new[2] = h42->face;
        f_new[3] = new_face();

        // 半边关系重建
        h14->face = f_new[1];
        h23->face = f_new[3];
        h31->prev = h[7];
        h31->next = h[0];
        h14->prev = h[1];
        h14->next = h[2];
        h42->prev = h[3];
        h42->next = h[4];
        h23->next = h[6];
        h23->prev = h[5];

        //(Halfedge *next, Halfedge *prev, Halfedge *inv, Vertex *from, Edge *edge, Face *face)
        h[0]->set_neighbors(h[7], h31, h[1], v1, e_new[0], f_new[0]);
        h[1]->set_neighbors(h14, h[2], h[0], v_new, e_new[0], f_new[1]);
        h[2]->set_neighbors(h[1], h14, h[3], v4, e_new[1], f_new[1]);
        h[3]->set_neighbors(h42, h[4], h[2], v_new, e_new[1], f_new[2]);
        h[4]->set_neighbors(h[3], h42, h[5], v2, e_new[2], f_new[2]);
        h[5]->set_neighbors(h23, h[6], h[4], v_new, e_new[2], f_new[3]);
        h[6]->set_neighbors(h[5], h23, h[7], v3, e_new[3], f_new[3]);
        h[7]->set_neighbors(h31, h[0], h[6], v_new, e_new[3], f_new[0]);

        // 顶点关系重建
        v1->halfedge = h[0];
        v2->halfedge = h[4];   
        v3->halfedge = h[6];
        v4->halfedge = h[2];

        v_new->halfedge = h[7];
        v_new->pos      = (v1->pos + v2->pos) / 2;
        v_new->is_new   = true;
        
        // 边关系重建
        for (int i = 0; i < 4; ++i) e_new[i]->halfedge = h[2 * i];
        e_new[1]->is_new = true;
        e_new[3]->is_new = true;
        
        // 面关系重建
        for (int i = 0; i < 4; ++i) f_new[i]->halfedge = h[2 * i];
        return v_new;
    }
}

optional<Vertex*> HalfedgeMesh::collapse_edge(Edge* e)
{
    

    if (e->on_boundary()) // 在边界上
    {
        Halfedge* h_cnt = e->halfedge;
        Vertex* v11     = h_cnt->from;
        Vertex* v22     = h_cnt->inv->from;
        // 检查是否会破坏流性
        int cnt       = 0;
        Halfedge* h11 = v11->halfedge;
        do {
            Vertex* neighbor_v1 = h11->inv->from;

            Halfedge* h22 = v22->halfedge;
            do {
                Vertex* neighbor_v2 = h22->inv->from;
                if (neighbor_v1->id == neighbor_v2->id)
                    cnt++;
                h22 = h22->inv->next;
            } while (h22 != v22->halfedge);

            h11 = h11->inv->next;
        } while (h11 != v11->halfedge);

        if (cnt != 1)
            return std::nullopt;

        Halfedge* h21 = e->halfedge;
        if (h21->is_boundary())
            h21 = h21->inv;
        
            

        Halfedge* h14 = h21->next;
        Halfedge* h42 = h14->next;

        Halfedge* h24 = h42->inv;
        Halfedge* h41 = h14->inv;

        Vertex* v4 = h42->from;
        Vertex* v2 = h21->from;
        Vertex* v1 = h14->from;

        Edge* e14 = h14->edge;
        Edge* e42 = h42->edge;

        Face* f2 = h21->face; 
        erase(f2);
        erase(e);
        erase(h21);
        erase(h21->inv);

        Vertex* v_new = new_vertex();

        Halfedge* h = v2->halfedge;
        do {
            h->from = v_new;
            h       = h->inv->next;
        } while (h != v2->halfedge);

        Halfedge* hh = v1->halfedge;
        do {
            hh->from = v_new;
            hh       = hh->inv->next;
        } while (hh != v1->halfedge);

        erase(v1);
        erase(v2);

        Edge* e_new = new_edge();

        h24->edge = e_new;
        h41->edge = e_new;

        h24->from = v_new;
        h41->from = v4;
        erase(e14);
        erase(e42);

        e_new->halfedge = h41;

        h41->inv = h24;
        h24->inv = h41;

        v_new->halfedge = h24;
        v4->halfedge    = h41;

        v_new->pos    = v_new->neighborhood_center();


        erase(h14);
        erase(h42);

        return v_new;
    } 
    else 
    {
        Halfedge* h_cnt = e->halfedge;
        Vertex* v11     = h_cnt->from;
        Vertex* v22     = h_cnt->inv->from;
        // 检查是否会破坏流性
        int cnt       = 0;
        Halfedge* h11 = v11->halfedge;
        do {
            Vertex* neighbor_v1 = h11->inv->from;

            Halfedge* h22 = v22->halfedge;
            do {
                Vertex* neighbor_v2 = h22->inv->from;
                if (neighbor_v1->id == neighbor_v2->id)
                    cnt++;
                h22 = h22->inv->next;
            } while (h22 != v22->halfedge);

            h11 = h11->inv->next;
        } while (h11 != v11->halfedge);

        if (cnt != 2)
            return std::nullopt;


        Halfedge* h12 = e->halfedge;
        Halfedge* h21 = h12->inv;
        Halfedge* h23 = h12->next;
        Halfedge* h31 = h23->next;
        Halfedge* h14 = h21->next;
        Halfedge* h42 = h14->next; // 这六条边全部删除

        Halfedge* h32 = h23->inv;
        Halfedge* h24 = h42->inv;
        Halfedge* h41 = h14->inv;
        Halfedge* h13 = h31->inv;

        Vertex* v4 = h42->from;
        Vertex* v3 = h31->from;
        Vertex* v2 = h21->from;
        Vertex* v1 = h12->from;

        Edge* e31 = h31->edge;
        Edge* e14 = h14->edge;
        Edge* e42 = h42->edge;
        Edge* e23 = h23->edge;

        Face* f1 = h31->face;
        Face* f2 = h14->face;

        erase(f1);
        erase(f2);
        erase(e);
        erase(h12);
        erase(h21);

        Vertex* v_new = new_vertex();

        Halfedge* h = v2->halfedge;
        do {
            h->from = v_new;
            h       = h->inv->next;
        } while (h != v2->halfedge);

        Halfedge* hh = v1->halfedge;
        do {
            hh->from = v_new;
            hh       = hh->inv->next;
        } while (hh != v1->halfedge);

        erase(v1);
        erase(v2);

        Edge* e_new[2];
        e_new[0] = new_edge();
        e_new[1] = new_edge();

        h32->edge = e_new[0];
        h13->edge = e_new[0];
        h24->edge = e_new[1];
        h41->edge = e_new[1];

        h32->from = v3;
        h13->from = v_new;
        h24->from = v_new;
        h41->from = v4;
        erase(e31);
        erase(e14);
        erase(e23);
        erase(e42);

        e_new[0]->halfedge = h32;
        e_new[1]->halfedge = h41;

        h13->inv = h32;
        h32->inv = h13;
        h41->inv = h24;
        h24->inv = h41;

        v3->halfedge = h32;
        v4->halfedge = h41;

        v_new->halfedge = h13;
        v_new->pos      = v_new->neighborhood_center();
        v_new->is_new   = true;

        erase(h31);
        erase(h14);
        erase(h42);
        erase(h23);

        return v_new;
    }
}
