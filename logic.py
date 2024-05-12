from gui import Ui_ContactBook, Ui_EditContactDialog, Ui_CreateContactDialog
from PyQt6 import QtWidgets, QtCore
import shutil, os

# Variable for setting save file
TXT_FILE = "contacts.txt"
# Defines the main temporary contacts dictionary, to be flushed to disk.
contacts = {}

class ContactBook(QtWidgets.QDialog, Ui_ContactBook):
    """
    This class contains all of the methods for the UI interactables.
    We tried tirelessly to get this to work outside of this file, but we could never get it down.
    """

    def __init__(self, parent=None):
        """Initialization for the ContactBook class."""
        global contacts
        super().__init__(parent)
        self.setupUi(self)
        contacts = load_contacts_from_txt()
        self.EditIDSelector.setValue(0)
        self.update_contact_list()
        self.CreateButton.clicked.connect(self.create_contact)
        self.EditIDButton.clicked.connect(self.edit_contact)

    def update_contact_list(self) -> None:
        """Updates the scroll area on the main UI to keep the contacts up-to-date."""
        # Clear the existing contact list contents
        if self.ContactListContents.layout():
            for i in reversed(range(self.ContactListContents.layout().count())):
                widget = self.ContactListContents.layout().itemAt(i).widget()
                if widget:
                    widget.deleteLater()
        else:
            # Create a vertical layout if one does not exist
            self.ContactListContents.setLayout(QtWidgets.QVBoxLayout())

        # Populate the contact list contents
        for contact_id, contact_info in contacts.items():
            contact_label = QtWidgets.QLabel(
                f"[{contact_id}] - {contact_info["firstname"]} {contact_info["lastname"]} - {contact_info["phone"]}, {contact_info["address"]}",
                parent=self.ContactListContents)
            self.ContactListContents.layout().addWidget(contact_label)

    def create_contact(self) -> None:
        """Initializes the UI used for creating a new contact."""
        print(f"[create_contact] starting contact creation dialog")
        self.create_contact_dialog = QtWidgets.QDialog()
        self.create_contact_ui = Ui_CreateContactDialog()
        self.create_contact_ui.setupUi(self.create_contact_dialog)
        self.create_contact_ui.C_CreateButton.clicked.connect(self.create_new_contact)
        self.create_contact_dialog.show()

    def create_new_contact(self) -> None:
        """Runs when the user presses the "Create" button in the contact creation dialog."""
        _translate = QtCore.QCoreApplication.translate
        print(f"[create_new_contact] getting info")
        first_name = self.create_contact_ui.C_FirstNameInput.toPlainText()
        last_name = self.create_contact_ui.C_LastNameInput.toPlainText()
        phone_number = self.create_contact_ui.C_PhnNmbrInput.toPlainText()
        address = self.create_contact_ui.C_AddrInput.toPlainText()

        # Checks to make sure the name fields aren't blank or numerical
        # We chose not to strip the input here due to some people having multiple names (for first/last),
        # separated by a space. Phone number and address can be left blank.
        if first_name.isalpha() and last_name.isalpha():
            self.create_contact_ui.C_ErrorLabel.setText(_translate("CreateContactDialog",
                                                                   "<html><head/><body><p><span style=\" font-size:10pt;\"> </span></p></body></html>"))
            print(f"[create_new_contact] creating dictionary for contact")
            new_contact = {
                "firstname": first_name,
                "lastname": last_name,
                "phone": phone_number,
                "address": address
            }
            try:
                contact_id = max(contacts.keys()) + 1
            except ValueError:
                contact_id = 0
            print(f"[create_new_contact] sending contact {contact_id} to add_contact")
            self.add_contact(contact_id, new_contact)
            print(f"[create_new_contact] finished, closing creation dialog")
            self.create_contact_dialog.close()
        else:
            print(f"[create_new_contact] invalid names provided, notifying user")
            self.create_contact_ui.C_ErrorLabel.setText(_translate("CreateContactDialog",
                                                                   "<html><head/><body><p><span style=\" font-size:10pt;\">Please enter valid first & last name(s).</span></p></body></html>"))

    def edit_contact(self) -> None:
        """Initializes the UI used for editing a contact."""
        print(f"[edit_contact] starting contact editing dialog")
        self.edit_contact_dialog = QtWidgets.QDialog()
        self.edit_contact_ui = Ui_EditContactDialog()
        self.edit_contact_ui.setupUi(self.edit_contact_dialog)
        self.edit_contact_dialog.show()
        self.id = self.EditIDSelector.value()
        _translate = QtCore.QCoreApplication.translate
        self.edit_contact_ui.E_IDLabel.setText(_translate("EditContactDialog", f"ID: {self.id}"))
        self.edit_contact_ui.E_SubmitButton.clicked.connect(self.submit_edit_contact)

    def submit_edit_contact(self) -> None:
        """This function is basically create_new_contact() with a few minor tweaks.
            Submits the edit to the dict and saves."""
        print(f"[submit_edit_contact] getting info")
        _translate = QtCore.QCoreApplication.translate
        first_name = self.edit_contact_ui.E_FirstNameInput.toPlainText()
        last_name = self.edit_contact_ui.E_LastNameInput.toPlainText()
        phone_number = self.edit_contact_ui.E_PhnNbrInput.toPlainText()
        address = self.edit_contact_ui.E_AddressInput.toPlainText()

        if first_name.isalpha() and last_name.isalpha():
            self.edit_contact_ui.E_IDLabel.setText(_translate("EditContactDialog",
                                                              f"<html><head/><body><p><span style=\" font-size:10pt;\">ID: {self.id}</span></p></body></html>"))
            print(f"[submit_edit_contact] creating dictionary for contact")
            edited_contact = {
                "firstname": first_name,
                "lastname": last_name,
                "phone": phone_number,
                "address": address
            }
            print(f"[submit_edit_contact] sending contact {self.id} to add_contact")
            self.add_contact(self.id, edited_contact)
            print(f"[submit_edit_contact] finished, closing editing dialog")
            self.edit_contact_dialog.close()
        else:
            print(f"[submit_edit_contact] invalid names provided, notifying user")
            self.edit_contact_ui.E_IDLabel.setText(_translate("EditContactDialog",
                                                              f"<html><head/><body><p><span style=\" font-size:10pt;\">Please enter valid first & last name(s).</span></p></body></html>"))

    def add_contact(self, contact_id, contact_info) -> None:
        """Simple function for adding the contact to the temporary dictionary,
        then saving the dictionary to the permanent .txt file."""
        print(f"[add_contact] adding contact {contact_id} to main dict")
        contacts[contact_id] = contact_info
        print(f"[add_contact] updating contact list on main UI")
        self.update_contact_list()
        print(f"[add_contact] using save_contacts_to_txt to save main dictionary")
        save_contacts_to_txt(contacts)


def load_contacts_from_txt() -> dict:
    """Loads contacts into the temporary dictionary from the file defined above."""
    contacts = {}
    try:
        with open(TXT_FILE, 'r') as file:
            for line in file:
                values = line.strip().split(',')  # Split the line by commas
                contact_id = int(values[0])  # Assuming the first value is the contact ID
                contact_info = {
                    'firstname': values[1],
                    'lastname': values[2],
                    'phone': values[3],
                    'address': values[4]
                }
                contacts[contact_id] = contact_info
        print("[load_contacts_from_txt] finished reading contacts from file")
        return contacts
    except FileNotFoundError:
        print("[load_contacts_from_txt] unable to read contacts from file (file missing), starting with blank dict")
        return {}
    except ValueError:
        print("[load_contacts_from_txt] unable to read contacts from file (data error), starting with blank dict")
        print("[load_contacts_from_txt] contact file will be purged from disk, a backup will be available however")
        shutil.copy("contacts.txt", "contacts.txt")
        os.remove("contacts.txt")
        return {}


def save_contacts_to_txt(contactsDict: dict) -> None:
    """Saves temporary contacts dictionary to a text file for permanent storage."""
    try:
        with open(TXT_FILE, 'w') as file:
            for contact_id, contact_data in contactsDict.items():
                file.write(
                    f"{contact_id},{contact_data['firstname']},{contact_data['lastname']},{contact_data['phone']},{contact_data['address']}\n")
        print(f"[save_contacts_to_txt] contacts saved to file successfully")
    except Exception as e:
        print(f"[save_contacts_to_txt] error saving contacts to file: \n{e}")
