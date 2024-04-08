from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError('Invalid phone number')


class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Incorrect format, Required format: DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if str(p) == old_phone:
                p.value = new_phone

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def find_next_birthday(self, weekday):
        today = datetime.now().date()
        next_birthday = None
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.date.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                if birthday_this_year.weekday() == weekday:
                    if next_birthday is None or birthday_this_year < next_birthday:
                        next_birthday = birthday_this_year
        return next_birthday

    def get_upcoming_birthday(self, days=7):
        upcoming_birthdays = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days)

        for record in self.data.values():
            if record.birthday:
                next_birthday_year = today.year if record.birthday.date.replace(
                    year=today.year) >= today else today.year + 1
                next_birthday = record.birthday.date.replace(year=next_birthday_year)
                if today <= next_birthday <= end_date:
                    upcoming_birthdays.append((record.name.value, next_birthday))

        return upcoming_birthdays


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "KeyError"
        except ValueError:
            return "ValueError"
        except IndexError:
            return "IndexError"

    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."



@input_error
def change_contact(args, book: AddressBook):
    if len(args) != 2:
        raise IndexError

    name, new_phone = args
    record = book.find(name)

    if record:
        old_phone = record.find_phone(new_phone)  # Знаходимо старий номер телефону для заміни
        if old_phone:
            record.edit_phone(old_phone.value, new_phone)
            return "Contact updated successfully"
        else:
            return "Contact not found."
    else:
        return "Contact not found."


@input_error
def show_phone(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError
    name = args[0]
    record = book.find(name)
    if record:
        return str(record)
    else:
        return "Contact not found."


@input_error
def show_all(book: AddressBook):
    if not book:
        return "No contacts found."
    else:
        return "\n".join([str(record) for record in book.values()])


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    message = "Birthday added."
    if record:
        record.add_birthday(birthday)
    else:
        message = "Contact not found."
    return message


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday.date.strftime('%d.%m.%Y')}"
    else:
        return "No birthday found for the contact."


@input_error
def birthdays(book):
    today = datetime.now().date()
    upcoming_birthdays = book.get_upcoming_birthday(days=7)
    birthdays_this_week = []

    for name, next_birthday in upcoming_birthdays:
        days_until_birthday = (next_birthday - today).days
        if days_until_birthday <= 7:
            birthdays_this_week.append((name, days_until_birthday))

    if birthdays_this_week:
        return "\n".join([f"{name}: {days} days left until birthday" for name, days in birthdays_this_week])
    else:
        return "No birthdays coming up in the next week."


def parse_input(user_input):
    parts = user_input.split(maxsplit=2)  # Додано maxsplit=2 для розділення на 3 частини максимум
    command = parts[0].lower()
    args = parts[1:]
    return command, args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()