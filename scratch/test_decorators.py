def login_required(func):
    def wrapper(*args, **kwargs):
        print("login_required check")
        return func(*args, **kwargs)
    return wrapper

def admin_required(f):
    @login_required
    def decorated(*args, **kwargs):
        print("admin check")
        return f(*args, **kwargs)
    return decorated

@admin_required
def my_func():
    print("my_func executed")

my_func()
