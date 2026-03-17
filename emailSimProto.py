import datetime
from dataclasses import dataclass, field
from typing import List, Optional

import streamlit as st


@dataclass
class Email:
    sender: str
    receiver: str
    subject: str
    body: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    read: bool = False

    def mark_as_read(self) -> None:
        self.read = True

    def preview(self) -> str:
        status = "Read" if self.read else "Unread"
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M")
        return f"[{status}] From: {self.sender} | Subject: {self.subject} | Time: {time_str}"


class Inbox:
    def __init__(self) -> None:
        self.emails: List[Email] = []

    def receive_email(self, email: Email) -> None:
        self.emails.append(email)

    def get_email(self, index: int) -> Optional[Email]:
        if 0 <= index < len(self.emails):
            return self.emails[index]
        return None

    def delete_email(self, index: int) -> bool:
        if 0 <= index < len(self.emails):
            del self.emails[index]
            return True
        return False


class User:
    def __init__(self, name: str) -> None:
        self.name = name
        self.inbox = Inbox()

    def send_email(self, receiver: "User", subject: str, body: str) -> None:
        email = Email(sender=self.name, receiver=receiver.name, subject=subject, body=body)
        receiver.inbox.receive_email(email)


# ---------- Session state setup ----------
def initialize_state() -> None:
    if "users" not in st.session_state:
        tory = User("Tory")
        ramy = User("Ramy")
        st.session_state.users = {
            "Tory": tory,
            "Ramy": ramy,
        }


    if "selected_user" not in st.session_state:
        st.session_state.selected_user = "Tory"

    if "selected_email_index" not in st.session_state:
        st.session_state.selected_email_index = None


# ---------- UI helpers ----------
def render_sidebar() -> None:
    st.sidebar.title("Email Simulator")
    st.sidebar.caption("A simple Streamlit email app built with Python OOP.")

    user_names = list(st.session_state.users.keys())
    current_index = user_names.index(st.session_state.selected_user)
    st.session_state.selected_user = st.sidebar.selectbox(
        "Current user",
        user_names,
        index=current_index,
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Create a new user")
    with st.sidebar.form("add_user_form", clear_on_submit=True):
        new_user_name = st.text_input("New username")
        submitted = st.form_submit_button("Add user")
        if submitted:
            cleaned = new_user_name.strip()
            if not cleaned:
                st.sidebar.error("Enter a username.")
            elif cleaned in st.session_state.users:
                st.sidebar.error("That user already exists.")
            else:
                st.session_state.users[cleaned] = User(cleaned)
                st.sidebar.success(f"Added user: {cleaned}")


# ---------- Main app ----------
def main() -> None:
    st.set_page_config(page_title= "Mini Email Simulator", layout="wide")
    initialize_state()
    render_sidebar()

    users = st.session_state.users
    current_user = users[st.session_state.selected_user]

    st.title("Mini Email Simulator")
    st.write("Send, open, and delete emails using a clickable interface.")

    send_col, inbox_col = st.columns([1, 1.2])

    with send_col:
        st.subheader("Send an email")
        with st.form("send_email_form", clear_on_submit=True):
            receiver_name = st.selectbox(
                "Receiver",
                [name for name in users.keys() if name != current_user.name],
                key="receiver_select",
            )
            subject = st.text_input("Subject")
            body = st.text_area("Body", height=180)
            send_pressed = st.form_submit_button("Send")

            if send_pressed:
                if not subject.strip() or not body.strip():
                    st.error("Subject and body cannot be empty.")
                else:
                    current_user.send_email(users[receiver_name], subject.strip(), body.strip())
                    st.success(f"Email sent from {current_user.name} to {receiver_name}!")

    with inbox_col:
        st.subheader(f"{current_user.name}'s Inbox")
        if not current_user.inbox.emails:
            st.info("This inbox is empty.")
        else:
            for idx, email in enumerate(current_user.inbox.emails):
                label = f"{idx + 1}. {email.preview()}"
                if st.button(label, key=f"open_{current_user.name}_{idx}"):
                    st.session_state.selected_email_index = idx

    st.markdown("---")
    st.subheader("Selected email")

    selected_index = st.session_state.selected_email_index
    selected_email = current_user.inbox.get_email(selected_index) if selected_index is not None else None

    if selected_email is None:
        st.write("Choose an email from the inbox to view it here.")
    else:
        selected_email.mark_as_read()
        with st.container(border=True):
            st.markdown(f"**From:** {selected_email.sender}")
            st.markdown(f"**To:** {selected_email.receiver}")
            st.markdown(f"**Subject:** {selected_email.subject}")
            st.markdown(
                f"**Received:** {selected_email.timestamp.strftime('%Y-%m-%d %H:%M')}"
            )
            st.markdown("**Body:**")
            st.write(selected_email.body)

        action_col1, action_col2 = st.columns([1, 4])
        with action_col1:
            if st.button("Delete email", type="primary"):
                deleted = current_user.inbox.delete_email(selected_index)
                if deleted:
                    st.session_state.selected_email_index = None
                    st.success("Email deleted.")
                    st.rerun()
        with action_col2:
            st.caption("Opening an email marks it as read.")


if __name__ == "__main__":
    main()
