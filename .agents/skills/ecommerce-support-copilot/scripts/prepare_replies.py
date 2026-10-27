"""Join support tickets to supplied orders and policies; create drafts without sending."""
from skill_io import index, rows, run


def process(data):
    orders = index(data.get("orders", []))
    tickets = rows(data.get("tickets", []), "tickets")
    index(tickets)
    policies = index(data.get("policies", []))
    output = []
    for ticket in tickets:
        item = {"ticket_id": str(ticket["id"]), "status": "needs_review", "draft": None,
                "actions": [], "sources": [], "facts": {}}
        order = orders.get(str(ticket.get("order_id", "")))
        if not order:
            item["actions"].append("request_order_reference")
        elif not ticket.get("customer_id") or ticket.get("customer_id") != order.get("customer_id"):
            item["actions"].append("verify_customer_order_match")
        else:
            item["sources"].append("order:" + str(order["id"]))
            item["facts"] = {k: order[k] for k in ("status", "tracking", "shipment_note") if k in order}
            intent = ticket.get("intent", "other")
            if intent == "order_status" and order.get("status"):
                item["draft"] = f"Your order {order['id']} is currently marked {order['status']}."
                if order.get("shipment_note"):
                    item["draft"] += " " + str(order["shipment_note"])
                item["status"] = "draft_ready"
                item["actions"].append("review_current_shipping_record_before_sending")
            elif intent in ("return", "cancellation"):
                policy = policies.get(str(ticket.get("policy_id", "")))
                if not policy or policy.get("approved") is not True:
                    item["actions"].append("request_approved_policy")
                elif policy.get("region") != order.get("region"):
                    item["actions"].append("resolve_policy_region_mismatch")
                else:
                    item["sources"].append("policy:" + str(policy["id"]))
                    item["facts"]["policy_text"] = policy.get("text", "")
                    item["draft"] = f"We have received your {intent} request for order {order['id']}. Our team will check it against the applicable policy."
                    item["actions"].append("human_review_eligibility_and_next_action")
            else:
                item["actions"].append("human_review_request")
        output.append(item)
    return {"tickets": output, "sent": False, "refunds_issued": False,
            "drafts_are_not_resolution_decisions": True}


if __name__ == "__main__":
    run(process, __doc__)
