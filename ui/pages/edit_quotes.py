import streamlit as st
from utils import *

def main():
    fetch_module_numbers()
    fetch_lect_ids()
    sort_lectures(st.session_state.lect_ids, st.session_state.module_numbers)
    collection_ref = st.session_state.db.collection("quotes")

    # Initialize quotes in session state
    if "quotes" not in st.session_state:
        docs = collection_ref.stream()
        st.session_state.quotes = [{"id": doc.id, "data": doc.to_dict()} for doc in docs]

    # Track modifications to efficiently update
    if "modified_quotes" not in st.session_state:
        st.session_state.modified_quotes = set()
    if "deleted_quotes" not in st.session_state:
        st.session_state.deleted_quotes = set()
    if "new_quotes" not in st.session_state:
        st.session_state.new_quotes = []

    setup("Edit Quotes")
    st.title("Edit Quotes")

    # Display and edit existing quotes
    if st.session_state.quotes:
        for i, item in enumerate(st.session_state.quotes):
            with st.expander(f"Quote {i+1}: {item['data']['quote']}"):
                # Store original value for comparison
                original_quote = item["data"]["quote"]
                edited_quote = st.text_area(f"Edit Quote {i+1}", original_quote, key=f"q_{i}")
                
                col1, col2, col3 = st.columns([1, 1, 10])
                with col1:
                    if st.button("Update", key=f"update_{i}"):
                        if edited_quote != original_quote:
                            st.session_state.quotes[i]["data"]["quote"] = edited_quote
                            if "id" in st.session_state.quotes[i]:
                                st.session_state.modified_quotes.add(st.session_state.quotes[i]["id"])
                            #st.success("Quote updated!")
                            st.rerun()
                with col2:
                    if st.button("Delete", key=f"delete_{i}"):
                        # Mark for deletion if it exists in database
                        if "id" in st.session_state.quotes[i]:
                            st.session_state.deleted_quotes.add(st.session_state.quotes[i]["id"])
                        st.session_state.quotes.pop(i)
                        st.rerun()
                with col3: st.empty()

    else:
        st.info("No quotes available. Add some quotes to get started.")

    # Add new quote
    with st.expander("Add New Quote"):
        new_quote = st.text_area("Quote")
        if st.button("Add Quote"):
            if new_quote:
                new_quote_data = {"data": {"quote": new_quote}}
                st.session_state.quotes.append(new_quote_data)
                st.session_state.new_quotes.append(new_quote_data)
                st.rerun()
            else:
                st.error("Quote is required.")

    # Save changes to database
    if st.button("Save All Changes"):
        with st.spinner("Saving changes..."):
            try:
                # Process deletions
                for quote_id in st.session_state.deleted_quotes:
                    collection_ref.document(quote_id).delete()
                
                # Process updates
                for item in st.session_state.quotes:
                    if "id" in item and item["id"] in st.session_state.modified_quotes:
                        collection_ref.document(item["id"]).set(item["data"])
                
                # Process new quotes
                for item in st.session_state.new_quotes:
                    new_doc_ref = collection_ref.add(item["data"])
                    item["id"] = new_doc_ref[1].id
                
                # Clear tracking sets
                st.session_state.modified_quotes = set()
                st.session_state.deleted_quotes = set()
                st.session_state.new_quotes = []
                
                st.success("All changes saved successfully!")
            except Exception as e:
                st.error(f"Error saving changes: {e}")

if __name__ == "__main__":
    main()