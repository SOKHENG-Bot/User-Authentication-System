

class UserService:
    
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_user_profile(self):
        pass

    async def update_user_profile(self):
        pass

    async def deactivate_account(self):
        pass

    async def delete_account(self):
        pass

    async def get_user_sessions(self):
        pass

    async def logout_all_devices(self):
        pass