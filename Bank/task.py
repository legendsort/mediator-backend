from Bank.services import BankService


def run_fetch_bank_data():
    bank_srv = BankService()
    bank_srv.fetch()


