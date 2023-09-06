import random
import string

def generate_random_password(length=25):
    # Define a pool of characters to choose from
    characters = string.ascii_letters + string.digits + string.punctuation

    # Generate a random password by selecting characters from the pool
    password = ''.join(random.choice(characters) for _ in range(length))

    return password


def generate_randomName():
    first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah"]
    last_names = ["Smith", "Johnson", "Brown", "Davis", "Wilson", "Lee"]
    random_first_name = random.choice(first_names)
    random_last_name = random.choice(last_names)
    random_full_name = f"{random_first_name}xyz461kssawsxmcns{random_last_name}"
    return random_full_name

def generate_randomEmail():
    name = generate_randomName()
    name += '@gmail.com'
    return name.replace(' ', '')

random_fullName = generate_randomName()
print(random_fullName)

random_password = generate_random_password()
print(random_password)


random_email = generate_randomEmail()
print(random_email)

