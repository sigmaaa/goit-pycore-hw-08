"""
Address Book Module

This module provides classes to create and manage an address book. The main
classes are:

- Field: Represents a generic field for storing values.
- Name: Represents a name field inheriting from the generic Field class.
- Phone: Represents a phone field inheriting from the generic Field class, with validation.
- Record: Represents a record in the address book, containing a name and multiple phone numbers.
- AddressBook: Represents an address book containing multiple records, with methods to add, 
find, and delete records.

"""

from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    """
    Represents a generic field for storing values.

    Attributes:
        value (str): The value of the field.
    """

    def __init__(self, value):
        """
        Initializes the field with the given value.

        Args:
            value (str): The value to be stored in the field.
        """
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Represents a name field inheriting from the generic Field class."""

    def __init__(self, name):
        super().__init__(name)
        if not name:
            raise ValueError("Name is a required field")


class Phone(Field):
    """
    Represents a phone field inheriting from the generic Field class.

    Attributes:
        phone_number (str): The phone number value.
    """

    def __init__(self, phone_number):
        """
        Initializes the phone field with the given phone number and validates it.

        Args:
            phone_number (str): The phone number to be stored in the field.
        """
        super().__init__(phone_number)
        self.__validate(phone_number)

    def __validate(self, phone_number):
        """
        Validates the phone number.

        Args:
            phone_number (str): The phone number to validate.

        Raises:
            ValueError: If the phone number is not valid.
        """
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise ValueError("Phone number must contain exactly 10 digits")

    def __format__(self, format_spec: str) -> str:
        return self.value.__format__(format_spec)


class Birthday(Field):
    """
    Represents a birthday in DD.MM.YYYY format. Contains validation
    """

    def __init__(self, value):
        """
        validates format and check if ensures that birthday is a date format
        """
        try:
            value = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError as exc:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from exc


class Record:
    """
    Represents a record in the address book.

    Attributes:
        name (Name): The name of the contact.
        phones (list of Phone): List of phone numbers associated with the contact.
    """

    def __init__(self, name):
        """
        Initializes a record with the given name.

        Args:
            name (str): The name of the contact.
        """
        self.name = Name(name)
        self.phones = []
        self.__birthday = None

    def add_birthday(self, birthday):
        """
        Adds a birthday to the contact.

        Args:
            birthday (str): The birthday to add in DD.MM.YYYY format.
        """
        self.__birthday = Birthday(birthday)

    @property
    def birthday(self):
        """
        Getter for Birthday object
        """
        return self.__birthday.value if self.__birthday is not None else None

    def add_phone(self, phone_number):
        """
        Adds a phone number to the contact.

        Args:
            phone_number (str): The phone number to add.
        """
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        """
        Removes a phone number from the contact.

        Args:
            phone_number (str): The phone number to remove.
        """
        self.phones = [
            phone for phone in self.phones if phone.value != phone_number]

    def edit_phone(self, old_phone_number, new_phone_number):
        """
        Edits a phone number in the contact.

        Args:
            old_phone_number (str): The phone number to be replaced.
            new_phone_number (str): The new phone number.
        """
        for phone in self.phones:
            if phone.value == old_phone_number:
                phone.value = new_phone_number

    def find_phone(self, phone_number):
        """
        Finds a phone number in the contact.

        Args:
            phone_number (str): The phone number to find.

        Returns:
            str: The found phone number or None if not found.
        """
        return next((phone.value for phone in self.phones if phone.value == phone_number), None)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    """
    Represents an address book containing multiple records.

    Methods:
        add_record(record): Adds a record to the address book.
        find(name): Finds a record by name.
        delete(name): Deletes a record by name.
    """

    def add_record(self, record):
        """
        Adds a record to the address book.

        Args:
            record (Record): The record to add.
        """
        self.data[record.name.value] = record

    def find(self, name):
        """
        Finds a record by name.

        Args:
            name (str): The name of the contact.

        Returns:
            Record: The found record or None if not found.
        """
        return self.data.get(name)

    def delete(self, name):
        """
        Deletes a record by name.

        Args:
            name (str): The name of the contact.
        """
        self.data.pop(name, None)

    def get_upcoming_birthdays(self):
        """
        Determine upcoming birthdays within the next 7 days for a list of users.

        :param users: List of dictionaries containing user information including name and birthday.
        :return: Dictionary mapping user names to their upcoming birthdays formatted as "%d.%m.%Y".
        """
        upcoming_birthdays = []
        current_date = datetime.today().date()

        for user in self.data.keys():
            user_birthday = self.data[user].birthday
            if user_birthday is None:
                continue
            user_birthday = user_birthday.replace(
                year=current_date.year)
            # Check if the birthday is within the next 7 days and not in the past
            if current_date < user_birthday <= current_date + timedelta(days=7):
                # Adjust on Monday if birthday falls on a weekend (Saturday or Sunday)
                if user_birthday.weekday() >= 5:
                    user_birthday += timedelta(7-user_birthday.weekday())

                upcoming_birthdays.append({
                    "name": user,
                    "congratulation_date:": user_birthday.strftime("%d.%m.%Y")
                })

        return upcoming_birthdays


def parse_input(user_input):
    """
    Parse user input into command and arguments.

    Parameters:
    user_input (str): The input string from the user.

    Returns:
    tuple: A tuple containing the command and a list of arguments.
    """
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def input_error(func):
    """
    Decorator for handling input error
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Error: Command requires exactly 2 arguments (name and phone/birthday)."
        except KeyError:
            return "Error: No contact with this name was found in the dictation"
        except IndexError:
            return "Error: Command requires 1 argument (name)"
    return inner


@input_error
def add_contact(args, contacts):
    """
    Add a new contact to the contacts dictionary.

    Parameters:
    args (list): A list of arguments containing the name and phone number.
    contacts (dict): The contacts dictionary.

    Returns:
    str: A message indicating the result of the operation.
    """
    name, phone, *_ = args
    record = contacts.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        contacts.add_record(record)
        message = "Contact added."
    if phone and record.find_phone(phone) is None:
        record.add_phone(phone)
    return message


@input_error
def get_number(args, contacts):
    """
    Returns a contact's phone from the dictionary.

    Parameters:
    args (list): A list of arguments containing the name.
    contacts (dict): The contacts dictionary.

    Returns:
    str: A message indicating the result of the operation.
    """
    name = args[0]
    return contacts[name]


@input_error
def change_contact(args, contacts):
    """
    Change the phone number for an existing contact.

    Parameters:
    args (list): A list of arguments containing the name and new phone number.
    contacts (dict): The contacts dictionary.

    Returns:
    str: A message indicating the result of the operation.
    """
    name, old_phone, new_phone = args
    contacts[name].edit_phone(old_phone, new_phone)
    return "Contact updated"


@input_error
def show_all(contacts):
    """
    Show all contacts in the contacts dictionary.

    Parameters:
    contacts (dict): The contacts dictionary.

    Returns:
    str: A formatted string of all contacts.
    """
    if not contacts:
        return "No contacts found."
    result = "\n" + "-" * 30 + "\n"
    result += f"{'Name':<15} {'Phone Number':<15}\n"
    result += "\n" + "-" * 30 + "\n"
    for name, record in contacts.items():
        for phone in record.phones:
            result += f"{name:<15} {phone:<15}\n"
            result += "\n"
    return result


@input_error
def add_birthday(args, contacts):
    """
    Adds a birthday to a contact in the AddressBook.

    Args:
        args (tuple): A tuple containing the name of the contact (str) and the birthday (str).
        contacts (AddressBook): The AddressBook object that contains the list of contacts.

    Returns:
        str: A message indicating that the birthday has been added for the specified contact.
    """
    name, birthday = args
    contacts[name].add_birthday(birthday)
    return f"Birthday has been added for {name}"


@input_error
def show_birthday(args, contacts):
    """
    Retrieves the birthday of a specific contact.

    Args:
        args (tuple): A tuple containing the name of the contact (str).
        contacts (AddressBook): The AddressBook object that contains the list of contacts.

    Returns:
        str: The birthday of the specified contact.
    """
    name = args[0]
    return contacts[name].birthday


@input_error
def birthdays(contacts):
    """
    Retrieves a list of upcoming birthdays from the AddressBook.

    Args:
        contacts (AddressBook): The AddressBook object that contains the list of contacts.

    Returns:
        list: A list of upcoming birthdays.
    """
    return contacts.get_upcoming_birthdays()


def save_data(book, filename="addressbook.pkl"):
    """
    Saves data into a file before closing the program
    """
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    """
    Loading data from the file during startup
    """
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    """
    Main function to run the assistant bot.
    """
    contacts = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        if command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "phone":
            print(get_number(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "all":
            print(show_all(contacts))
        elif command == "add-birthday":
            print(add_birthday(args, contacts))
        elif command == "show-birthday":
            print(show_birthday(args, contacts))
        elif command == "birthdays":
            print(birthdays(contacts))
        else:
            print("Invalid command.")
    save_data(contacts)


if __name__ == "__main__":
    main()
