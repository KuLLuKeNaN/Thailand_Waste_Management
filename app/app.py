import json
import os
from datetime import date, timedelta
from uuid import uuid4

import pandas as pd
import streamlit as st

DATA_DIR = "data"
LISTINGS_FILE = os.path.join(DATA_DIR, "listings.json")
SUBSCRIBERS_FILE = os.path.join(DATA_DIR, "subscribers.json")


def ensure_file(path):
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_json(path):
    ensure_file(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def clear_listings():
    save_json(LISTINGS_FILE, [])


def delete_listing_by_id(listing_id: str):
    listings = load_json(LISTINGS_FILE)
    listings = [l for l in listings if l.get("id") != listing_id]
    save_json(LISTINGS_FILE, listings)


st.set_page_config(page_title="Thailand Waste Exchange", layout="wide")
st.title("♻️ Thailand Waste Exchange")
st.caption("Prototype – organic waste redistribution")

tab_dashboard, tab_create, tab_browse, tab_notify = st.tabs(
    ["📊 Dashboard", "➕ Create Listing", "📋 Browse & Claim", "🔔 Notifications"]
)

# ---------------- DASHBOARD ----------------
with tab_dashboard:
    listings = load_json(LISTINGS_FILE)

    if not listings:
        st.info("No listings yet.")
    else:
        df = pd.DataFrame(listings)
        df["available_date"] = pd.to_datetime(df["available_date"]).dt.date

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total listings", len(df))
        c2.metric("Available", int((df["status"] == "available").sum()))
        c3.metric("Claimed", int((df["status"] == "claimed").sum()))
        c4.metric("Total kg", int(df["quantity"].sum()))

        st.bar_chart(df.groupby("waste_type")["quantity"].sum())


# ---------------- CREATE LISTING ----------------
with tab_create:
    with st.form("create_form", clear_on_submit=True):
        org_name = st.text_input("Organization name")
        waste_type = st.selectbox(
            "Waste type",
            ["Banana peels", "Food scraps", "Coffee grounds", "Used cooking oil"]
        )
        quantity = st.number_input("Quantity (kg)", min_value=1)
        available_date = st.date_input("Available date", value=date.today())
        location = st.text_input("Location")
        submit = st.form_submit_button("Create")

    if submit:
        if not org_name or not location:
            st.error("Organization name and location are required.")
        else:
            listings = load_json(LISTINGS_FILE)
            listings.append({
                "id": str(uuid4()),
                "org_name": org_name,
                "waste_type": waste_type,
                "quantity": int(quantity),
                "available_date": available_date.isoformat(),
                "location": location,
                "status": "available",
                "claimed_by": None
            })
            save_json(LISTINGS_FILE, listings)
            st.success("Listing created ✅")
            st.rerun()


# ---------------- BROWSE & CLAIM ----------------
with tab_browse:
    st.subheader("Listings")

    listings = load_json(LISTINGS_FILE)

    if not listings:
        st.info("No listings.")
    else:
        for item in listings:
            with st.container(border=True):
                st.markdown(f"### {item['waste_type']} — {item['quantity']} kg")
                st.write(f"Org: {item['org_name']} | Date: {item['available_date']}")
                st.write(f"Location: {item['location']}")
                st.write(f"Status: `{item['status']}`")

                col1, col2 = st.columns([1, 1])

                with col1:
                    if item["status"] == "available":
                        claimer = st.text_input("Claimed by", key=f"claimer_{item['id']}")
                        if st.button("Claim", key=f"claim_{item['id']}"):
                            if not claimer:
                                st.warning("Enter a name to claim.")
                            else:
                                item["status"] = "claimed"
                                item["claimed_by"] = claimer
                                save_json(LISTINGS_FILE, listings)
                                st.success("Claimed ✅")
                                st.rerun()
                    else:
                        st.write(f"Claimed by: **{item.get('claimed_by') or '-'}**")

                with col2:
                    if st.button("Delete", key=f"del_{item['id']}"):
                        delete_listing_by_id(item["id"])
                        st.success("Deleted ✅")
                        st.rerun()


# ---------------- NOTIFICATIONS ----------------
with tab_notify:
    st.subheader("Community Center Subscriptions")

    subscribers = load_json(SUBSCRIBERS_FILE)

    with st.form("sub_form", clear_on_submit=True):
        name = st.text_input("Center name")
        interests = st.multiselect(
            "Interested waste types",
            ["Banana peels", "Food scraps", "Coffee grounds", "Used cooking oil"]
        )
        sub_btn = st.form_submit_button("Subscribe")

    if sub_btn:
        if not name or not interests:
            st.warning("Please enter a center name and select at least one waste type.")
        else:
            subscribers.append({"name": name, "interests": interests})
            save_json(SUBSCRIBERS_FILE, subscribers)
            st.success("Subscribed successfully 🔔")
            st.rerun()

    st.divider()
    st.subheader("Send notifications (simulation)")

    notify_date = st.date_input("Notify for date", value=date.today() + timedelta(days=1))
    listings = load_json(LISTINGS_FILE)

    target_listings = [
        l for l in listings
        if l["available_date"] == notify_date.isoformat()
        and l["status"] == "available"
    ]

    st.write(f"Subscribers: **{len(subscribers)}**")
    st.write(f"Available listings on {notify_date.isoformat()}: **{len(target_listings)}**")

    if st.button("Send notifications"):
        if not subscribers:
            st.warning("No subscribers found. Add a community center subscription first.")
        elif not target_listings:
            st.info("No available listings for the selected date.")
        else:
            sent_count = 0
            for sub in subscribers:
                matched = [
                    l for l in target_listings
                    if l["waste_type"] in sub["interests"]
                ]

                if matched:
                    sent_count += 1
                    st.success(f"🔔 Sent to {sub['name']} — {len(matched)} match(es)")
                    for m in matched:
                        st.write(f"- {m['waste_type']} ({m['quantity']} kg) from {m['org_name']} @ {m['location']}")
                else:
                    st.write(f"⚪ No matches for {sub['name']}")

            st.info(f"Done. Notifications sent to **{sent_count}** subscriber(s).")

    st.divider()
    st.subheader("Danger zone")

    colA, colB = st.columns(2)
    with colA:
        if st.button("Clear ALL listings"):
            clear_listings()
            st.success("All listings cleared ✅")
            st.rerun()

    with colB:
        if st.button("Clear ALL subscribers"):
            save_json(SUBSCRIBERS_FILE, [])
            st.success("All subscribers cleared ✅")
            st.rerun()
