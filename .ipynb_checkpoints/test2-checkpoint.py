import ipywidgets as widgets
from IPython.display import display, clear_output

class MLMSystem:
    def __init__(self):
        # Menyimpan informasi pengguna dengan jumlah staking dan komisi yang diterima
        self.users = {}
        # Menyimpan pohon referral
        self.referrals = {}

    def add_user(self, user_id, staking_amount, referrer=None):
        """Menambahkan pengguna baru dengan jumlah staking dan referrer."""
        self.users[user_id] = {
            'staking': staking_amount,
            'commission': 0
        }
        if referrer:
            if referrer in self.referrals:
                self.referrals[referrer].append(user_id)
            else:
                self.referrals[referrer] = [user_id]

    def calculate_rewards(self):
        """Menghitung rewards dan komisi untuk semua pengguna."""
        # Menghitung reward staking
        for user, details in self.users.items():
            details['commission'] += details['staking'] * 0.12  # 12% dari staking

        # Menghitung komisi referral
        for referrer, referrals in self.referrals.items():
            for level, referral in enumerate(referrals):
                if level < 3:  # Hanya hingga 3 level referral
                    # Komisi untuk yang mengajak
                    self.users[referrer]['commission'] += self.users[referral]['staking'] * 0.05  # 5% komisi
                    # Komisi royalti untuk yang mengajak sebelumnya (hingga 2 level sebelumnya)
                    current_referrer = referrer
                    for i in range(2):
                        if current_referrer in self.referrals:
                            parent_referrer = next((key for key, value in self.referrals.items() if current_referrer in value), None)
                            if parent_referrer:
                                if i == 0:
                                    self.users[parent_referrer]['commission'] += self.users[referral]['staking'] * 0.03  # 3% royalti
                                elif i == 1:
                                    self.users[parent_referrer]['commission'] += self.users[referral]['staking'] * 0.02  # 2% royalti
                                current_referrer = parent_referrer

    def get_commission_report(self):
        """Mengembalikan laporan komisi untuk setiap pengguna."""
        return {user: details['commission'] for user, details in self.users.items()}

class MLMSystemInteractive(MLMSystem):
    def __init__(self):
        super().__init__()
        self.output_area = widgets.Output()
        self.create_widgets()

    def create_widgets(self):
        """Membuat widgets untuk input dan aksi."""
        self.user_id_input = widgets.Text(description="User ID:")
        self.staking_input = widgets.FloatText(description="Staking Amount:")
        self.referrer_input = widgets.Text(description="Referrer ID:", placeholder="Optional")
        self.add_user_button = widgets.Button(description="Add User")
        self.calculate_rewards_button = widgets.Button(description="Calculate Rewards")
        self.add_user_button.on_click(self.add_user_action)
        self.calculate_rewards_button.on_click(self.calculate_rewards_action)
        
        display(self.user_id_input, self.staking_input, self.referrer_input,
                self.add_user_button, self.calculate_rewards_button, self.output_area)

    def add_user_action(self, b):
        """Aksi untuk menambahkan pengguna."""
        user_id = self.user_id_input.value
        staking = self.staking_input.value
        referrer = self.referrer_input.value or None
        self.add_user(user_id, staking, referrer)
        with self.output_area:
            clear_output(wait=True)
            print(f"Added user {user_id} with staking {staking} and referrer {referrer}")

    def calculate_rewards_action(self, b):
        """Aksi untuk menghitung dan menampilkan rewards."""
        self.calculate_rewards()
        commission_report = self.get_commission_report()
        with self.output_area:
            clear_output(wait=True)
            print("Commission Report:")
            for user, commission in commission_report.items():
                print(f"{user}: ${commission:.2f}")

# Membuat instance MLMSystemInteractive dan menampilkan interface
mlm_interactive = MLMSystemInteractive()
