import random
import string
from datetime import datetime

def generate_reference_id():
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"NGOPIPAY-{date_str}-{random_str}"