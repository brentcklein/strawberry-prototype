from app.types import Company, UserGroup, User

# Define some testing data
xometry = Company(name='Xometry')

xometry.user_groups.append(UserGroup(name='admins'))
xometry.user_groups.append(UserGroup(name='customers'))

admin_group = xometry.user_groups[0]
admins = admin_group.users
admins.append(User(name="Bob", age=50, nickname=None))
admins.append(User(name="Joe", age=30, nickname="Joey"))

customer_group = xometry.user_groups[1]
customers = customer_group.users
customers.append(User(name="Sally", age=40, nickname=None))
customers.append(User(name="Bill", age=35, nickname="Billy"))
