void HalfedgeMesh::smooth()
{
    optional<HalfedgeMeshFailure> check_result = validate();
    if (check_result.has_value()) {
        return;
    }
    
    for (Vertex* v = vertices.head; v != nullptr; v = v->next_node) 
    {
        Halfedge* h_loop = v->halfedge;
        double lambda    = 0.4; 
        Vector3f sv;
        sv.setZero();
        double w_sum = 0.0;
        do 
        {
            Vertex* v_i  = h_loop->inv->from;
            Vertex* v_i1 = h_loop->inv->next->inv->from;
            Vertex* v_i0 = h_loop->prev->from;

            Vector3f v_i_v_i1 = v_i->pos - v_i1->pos; // 向量 v_i 到 v_{i+1}
            Vector3f v_v_i1   = v->pos - v_i1->pos;   // 向量 v 到 v_{i+1}
            v_i_v_i1          = v_i_v_i1.normalized();
            v_v_i1            = v_v_i1.normalized();
            double cosa       = v_i_v_i1.dot(v_v_i1);
            double sina       = sqrt(1 - (cosa * cosa));
            double cota       = cosa / sina;

            Vector3f v_i_v_i0 = v_i->pos - v_i0->pos; // 向量 v_i 到 v_{i+1}
            Vector3f v_v_i0   = v->pos - v_i0->pos;   // 向量 v 到 v_{i+1}
            v_i_v_i0          = v_i_v_i0.normalized();
            v_v_i0            = v_v_i0.normalized();
            double cosb       = v_i_v_i0.dot(v_v_i0);
            double sinb       = sqrt(1 - (cosb * cosb));
            double cotb       = cosb / sinb;

            w_sum += 0.5 * (cota + cotb);
            sv += 0.5 * (cota + cotb) * (v_i->pos - v->pos);
            h_loop = h_loop->inv->next;
        } while (h_loop != v->halfedge);
        
        
        
        v->new_pos                                 = v->pos + lambda / w_sum * sv;
    }

    for (Vertex* v = vertices.head; v != nullptr; v = v->next_node) v->pos = v->new_pos;
    global_inconsistent = true;
    validate();
}

void Toolbar::model_mode(Scene& scene)
{
    if (ImGui::BeginTabItem("Model")) {
        mode = WorkingMode::MODEL;

        bool no_halfedge_mesh = !scene.halfedge_mesh;
        bool halfedge_mesh_failed =
            scene.halfedge_mesh && scene.halfedge_mesh->error_info.has_value();
        if (no_halfedge_mesh || halfedge_mesh_failed) {
            if (no_halfedge_mesh) {
                ImGui::TextWrapped("No halfedge mesh has been built yet");
            }
            if (halfedge_mesh_failed) {
                ImGui::TextWrapped(
                    "Failed to build a halfedge mesh for the current"
                    "object, or the halfedge mesh was broken by some invalid operation");
            }
            ImGui::Text("No operation available");
            ImGui::EndTabItem();
            return;
        }

        ImGui::SeparatorText("Local Operations");
        if (holds_alternative<const Halfedge*>(selected_element)) {
            const Halfedge* h = std::get<const Halfedge*>(selected_element);
            ImGui::Text("Halfedge (ID: %zu)", h->id);
            if (ImGui::Button("Inverse")) {
                const Halfedge* t = h->inv;
                if (!(t->is_boundary())) {
                    on_element_selected(t);
                }
            }
            ImGui::SameLine();
            if (ImGui::Button("Next")) {
                on_element_selected(h->next);
            }
            ImGui::SameLine();
            if (ImGui::Button("Previous")) {
                on_element_selected(h->prev);
            }
            if (ImGui::Button("From")) {
                on_element_selected(h->from);
            }
            ImGui::SameLine();
            if (ImGui::Button("Edge")) {
                on_element_selected(h->edge);
            }
            ImGui::SameLine();
            if (ImGui::Button("Face")) {
                on_element_selected(h->face);
            }
        } else if (holds_alternative<Vertex*>(selected_element)) {
            Vertex* v = std::get<Vertex*>(selected_element);
            ImGui::Text("Vertex (ID: %zu)", v->id);
            Vector3f& position = v->pos;
            if (ImGui::Button("Halfedge")) {
                on_element_selected(v->halfedge);
            }
            ImGui::Text("Position");
            ImGui::PushID("Selected Vertex##");
            xyz_drag(&position.x(), &position.y(), &position.z(), POSITION_UNIT);
            ImGui::PopID();
        } else if (holds_alternative<Edge*>(selected_element)) {
            Edge* e = std::get<Edge*>(selected_element);
            ImGui::Text("Edge (ID: %zu)", e->id);
            Vector3f center = e->center();
            if (ImGui::Button("Halfedge")) {
                on_element_selected(e->halfedge);
            }
            if (ImGui::Button("Flip")) {
                optional<Edge*> result = scene.halfedge_mesh->flip_edge(e);
                if (result.has_value()) {
                    scene.halfedge_mesh->global_inconsistent = true;
                }
            }
            ImGui::SameLine();
            if (ImGui::Button("Split")) {
                on_selection_canceled();
                optional<Vertex*> result = scene.halfedge_mesh->split_edge(e);
                if (result.has_value()) {
                    scene.halfedge_mesh->global_inconsistent = true;
                    on_element_selected(result.value());
                }
            }
            ImGui::SameLine();
            if (ImGui::Button("Collapse")) {
                on_selection_canceled();
                optional<Vertex*> result = scene.halfedge_mesh->collapse_edge(e);
                if (result.has_value()) {
                    scene.halfedge_mesh->global_inconsistent = true;
                    on_element_selected(result.value());
                }
            }
            ImGui::Text("Position");
            ImGui::PushID("Selected Edge##");
            xyz_drag(&center.x(), &center.y(), &center.z(), POSITION_UNIT);
            ImGui::PopID();
            // Only sync the positions of endpoints if no local operation has been performed.
            // Because an local operation makes the halfedge mesh and the mesh inconsistent,
            // and no modification should take place at the inconsistent state.
            if (!scene.halfedge_mesh->global_inconsistent) {
                Vector3f delta = center - e->center();
                Vertex* v1     = e->halfedge->from;
                Vertex* v2     = e->halfedge->inv->from;
                v1->pos += delta;
                v2->pos += delta;
            }
        } else if (holds_alternative<Face*>(selected_element)) {
            Face* f = std::get<Face*>(selected_element);
            ImGui::Text("Face (ID: %zu)", f->id);
            Vector3f center = f->center();
            if (ImGui::Button("Halfedge")) {
                on_element_selected(f->halfedge);
            }
            ImGui::Text("Position");
            ImGui::PushID("Selected Face##");
            xyz_drag(&center.x(), &center.y(), &center.z(), POSITION_UNIT);
            ImGui::PopID();
            Vector3f delta = center - f->center();
            Halfedge* h    = f->halfedge;
            do {
                h->from->pos += delta;
                h = h->next;
            } while (h != f->halfedge);
        }

        ImGui::SeparatorText("Global Operations");
        if (ImGui::Button("Loop Subdivide")) {
            scene.halfedge_mesh->loop_subdivide();
        }
        ImGui::SameLine();
        if (ImGui::Button("Smooth")) {
            scene.halfedge_mesh->smooth();
        }
        ImGui::SameLine();
        if (ImGui::Button("Simplify")) {
            scene.halfedge_mesh->simplify();
        }
        ImGui::SameLine();
        if (ImGui::Button("Isotropic Remesh")) {
            scene.halfedge_mesh->isotropic_remesh();
        }

        ImGui::EndTabItem();
    }
}