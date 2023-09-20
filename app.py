import click

from main import app, db_session, User


@app.cli.command("delete-user")
@click.option("--username", prompt="Username", help="The username of the user to delete.")
def delete_user(username):
    user = db_session.query(User).filter_by(username=username).first()
    if user:
        db_session.delete(user)
        db_session.commit()
        click.echo(f"User {username} deleted successfully.")
    else:
        click.echo("User not found.")


@app.cli.command("list-users")
def list_users():
    users = db_session.query(User).all()
    if users:
        click.echo("Current users:")
        for user in users:
            click.echo(f"Username: {user.username}, Email: {user.email}")
    else:
        click.echo("No users found.")


@app.cli.command("create-user")
@click.option("--username", prompt="Username", help="The username for the new user.")
@click.option("--email", prompt="Email", help="The email address for the new user.")
@click.option("--password", prompt="Password", hide_input=True, confirmation_prompt=True, help="The password for the new user.")
def create_user(username, email, password):
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db_session.add(new_user)
    db_session.commit()
    click.echo(f"User {username} created successfully.")
