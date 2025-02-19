void HalfedgeMesh::loop_subdivide()
{
    optional<HalfedgeMeshFailure> check_result = validate();
    if (check_result.has_value()) {
        return;
    }
    logger->info("subdivide object {} (ID: {}) with Loop Subdivision strategy", object.name,
                 object.id);
    logger->info("original mesh: {} vertices, {} faces in total", vertices.size, faces.size);

    for (Vertex* v = vertices.head; v != nullptr; v = v->next_node) {
        v->is_new = false;

        bool v_on_b = false;

        Halfedge* h22 = v->halfedge;
        do {  
            if (h22->inv->is_boundary() || h22->is_boundary())
            {
                v_on_b = true;
                break;
            }
            h22 = h22->inv->next;
        } while (h22 != v->halfedge);

        if (!v_on_b)
        {
            size_t n = v->degree();
            double u;
            if (n == 3)
                u = 3.0 / 16.0;
            else
                u = 3.0 / (8.0 * double(n));

            v->new_pos = (1 - double(n) * u) * v->pos + u * n * v->neighborhood_center();
        } 
        else
        {
            Halfedge* h33 = v->halfedge;
            do {
                if (h33->inv->is_boundary() || h33->is_boundary()) 
                {
                    v->new_pos = v->pos;
                    
                    if (h33->is_boundary())
                    {
                        Vertex* v11 = h33->inv->from;
                        Vertex* v22 = h33->prev->from;
                        v->new_pos  = (3.0 / 4.0) * v->pos + (1.0 / 8.0) * (v11->pos + v22->pos);
                    }
                    if (h33->inv->is_boundary())
                    {
                        Vertex* v11 = h33->inv->from;
                        Vertex* v22 = h33->inv->next->inv->from;
                        v->new_pos  = (3.0 / 4.0) * v->pos + (1.0 / 8.0) * (v11->pos + v22->pos);
                    }

                    break;
                }
                h33 = h33->inv->next;
            } while (h33 != v->halfedge);
        }
    }

    for (Edge* e = edges.head; e != nullptr; e = e->next_node) {
        e->is_new = false;

        if (!e->on_boundary())
        {
            e->new_pos =
                e->center() * 2 * 3 / 8 +
                (e->halfedge->next->next->from->pos + e->halfedge->inv->next->next->from->pos) / 8;
        }
        else
        {
            e->new_pos = e->center();
        }
    }

    size_t n = edges.size;
    for (Edge* e = edges.head; e != nullptr && n != 0; e = e->next_node) 
    {
        if (e->is_new == false)
        {
            Vertex* v  = split_edge(e).value();
            v->new_pos = e->new_pos;
        }    
        n--;     
    }


    for (Edge* e = edges.head; e != nullptr; e = e->next_node) {
        if (e->is_new) {
            Vertex* v1 = e->halfedge->from;
            Vertex* v2 = e->halfedge->inv->from;
            if (v1->is_new ^ v2->is_new)
                flip_edge(e);
        }
    }

    for (Vertex* v = vertices.head; v != nullptr; v = v->next_node) v->pos = v->new_pos;

    global_inconsistent = true;
    logger->info("subdivided mesh: {} vertices, {} faces in total", vertices.size, faces.size);
    logger->info("Loop Subdivision done");
    logger->info("");
    validate();
}
