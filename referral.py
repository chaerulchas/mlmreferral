import networkx as nx
import matplotlib.pyplot as plt

import ipywidgets as widgets
from IPython.display import display, clear_output

class MLMSystem:
    def __init__(self):
        # Menyimpan informasi pengguna termasuk staking dan komisi yang diterima
        self.users = {}
        # Menyimpan struktur pohon referral
        self.referrals = {}
        self.days = 0

    def add_user(self, user_id, user_name, staking_amount, referrer=None):
        """Menambahkan pengguna baru dengan nama, jumlah staking, dan referrer."""
        self.users[user_id] = {
            'name': user_name,
            'staking': staking_amount,
            'base_reward': 0,  # Reward dasar dari staking
            'commission': 0,  # Komisi dari referral
            'total_reward': 0,  # Total reward setelah komisi
            'referrer_fee': 0 # Total jumlah referral fee yang di bagikan
        }
        if referrer:
            if referrer in self.referrals:
                self.referrals[referrer].append(user_id)
            else:
                self.referrals[referrer] = [user_id]

    def total_staked(self):
        """Menghitung jumlah total yang di-stake oleh semua pengguna."""
        total = sum(user['staking'] for user in self.users.values())
        return total

    def calculate_rewards(self, days):
        """Menghitung reward dan komisi untuk semua pengguna."""
        # Menghitung reward staking
        self.days = days
        for user, details in self.users.items():
            details['base_reward'] = details['staking'] * 0.12 / 365 * days  # 12% per tahun dari staking

        # Reset komisi dan total reward setiap kali fungsi ini dipanggil
        for user in self.users.values():
            user['commission'] = 0
            user['total_reward'] = 0
            user['referrer_fee'] = 0

        # Menghitung komisi referral
        for referrer, referrals in self.referrals.items():
            for level, referral in enumerate(referrals):
                referral_reward = self.users[referral]['base_reward']
                print(referrals)
                  # Hanya sampai 3 level referral
                if level < 3:  # Hanya sampai 3 level referral
                    # Mengurangi komisi dari reward staking pengguna yang direferensikan
                    commission = referral_reward * 0.05  # 5% komisi
                    self.users[referrer]['commission'] += commission  # Menambahkan ke pengguna yang mereferensikan
                    self.users[referral]['referrer_fee'] += commission  # Mengunrangkan Komisi dari reward staking pengguna yang direferensikan
                    # Komisi royalti untuk yang mereferensikan di atasnya (sampai 2 level di atas)
                    current_referrer = referrer
                    for i in range(2):
                        if current_referrer in self.referrals:
                            parent_referrer = next((key for key, value in self.referrals.items() if current_referrer in value), None)
                            if parent_referrer:
                                royalty = referral_reward * (0.03 if i == 0 else 0.02)  # 3% atau 2% royalti
                                self.users[parent_referrer]['commission'] += royalty
                                self.users[referral]['referrer_fee'] += royalty  # Mengunrangkan Royalti dari reward staking pengguna yang direferensikan
                                current_referrer = parent_referrer

        # Menambahkan reward dasar dan komisi untuk mendapatkan total reward
        for user, details in self.users.items():
            details['total_reward'] = details['base_reward'] + details['commission'] - details['referrer_fee']


    def get_commission_report(self):
        """Mengembalikan laporan komisi untuk setiap pengguna, termasuk stake mereka."""
        return {user: {'Stake': details['staking'], 'Total Reward': details['total_reward'], 'Base Reward': details['base_reward'], 'Commission': details['commission']} for user, details in self.users.items()}

class MLMSystemInteractive(MLMSystem):
    def __init__(self):
        super().__init__()
        self.output_area = widgets.Output()
        self.graph_area = widgets.Output()
        self.create_widgets()

    def create_widgets(self):
        """Membuat widget untuk input dan aksi."""
        self.user_id_input = widgets.Text(description="User ID:")
        self.user_name_input = widgets.Text(description="Nama User:")  # Widget input nama pengguna
        self.staking_input = widgets.FloatText(description="Jumlah Staking:")
        self.referrer_input = widgets.Text(description="ID Referrer:", placeholder="Opsional")
        self.add_user_button = widgets.Button(description="Tambah User")
        self.days_spent = widgets.FloatText(description="Hari Berlalu:")
        self.calculate_rewards_button = widgets.Button(description="Hitung Reward")
        self.add_user_button.on_click(self.add_user_action)
        self.calculate_rewards_button.on_click(self.calculate_rewards_action)
        
        display(widgets.VBox([self.user_id_input, self.user_name_input, self.staking_input, self.referrer_input,
                              self.add_user_button, self.days_spent, self.calculate_rewards_button,
                              self.output_area, self.graph_area]))

    def draw_graph(self):
        """Draw a referral network graph using a tree layout."""
        with self.graph_area:
            clear_output(wait=True)
            G = nx.DiGraph()

            # Building the graph nodes and edges from the referral data
            for referrer, referrals in self.referrals.items():
                for referral in referrals:
                    referrer_data = self.users[referrer]
                    referrer_label = f"{referrer_data['name']} ({referrer})\nStake: {referrer_data['staking']}\nReward: {referrer_data['total_reward']:.2f}\nCommission: {referrer_data['commission']:.2f}"
                    
                    referral_data = self.users[referral]
                    referral_label = f"{referral_data['name']} ({referral})\nStake: {referral_data['staking']}\nReward: {referral_data['total_reward']:.2f}\nCommission: {referral_data['commission']:.2f}"
                    
                    G.add_node(referrer_label)  # Add referrer node
                    G.add_node(referral_label)  # Add referral node
                    G.add_edge(referrer_label, referral_label)  # Add edge between referrer and referral

            # Use Graphviz to create a tree layout
            try:
                pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
            except ImportError:
                print("PyGraphviz is not installed. Falling back to planar layout.")
                pos = nx.planar_layout(G)

            plt.figure(figsize=(12, 8))
            nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=5000, alpha=0.6,
                    font_size=12, font_weight='bold', edge_color='darkblue', width=2, arrowstyle='-|>', arrowsize=15)
            plt.title('Referral Network Tree Graph')
            plt.axis('off')  # Hide the axes
            plt.show()




    def add_user_action(self, b):
        """Aksi menambahkan pengguna dengan nama."""
        user_id = self.user_id_input.value
        user_name = self.user_name_input.value
        staking = self.staking_input.value
        referrer = self.referrer_input.value or None
        if user_id and user_name and staking > 0:
            self.add_user(user_id, user_name, staking, referrer)
            with self.output_area:
                clear_output(wait=True)
                print(f"User ditambahkan: {user_name} ({user_id}) dengan staking {staking} dan referrer {referrer}")
            self.draw_graph()
        else:
            with self.output_area:
                clear_output(wait=True)
                print("Mohon masukkan detail pengguna yang valid.")

    def calculate_rewards_action(self, b):
        """Aksi untuk menghitung dan menampilkan reward, komisi, dan stake pengguna serta total staked."""
        days_spent = self.days_spent.value
        if days_spent > 0:
            self.calculate_rewards(days_spent)
            commission_report = self.get_commission_report()
            total_staked = self.total_staked()
            with self.output_area:
                clear_output(wait=True)
                print(f"Laporan Komisi setelah {self.days} hari:")
                print(f"Total Staked Keseluruhan: ${total_staked:.2f}\n")
                for user, details in commission_report.items():
                    print(f"{user}: Stake: {details['Stake']:.2f} DNY, Total Reward: {details['Total Reward']:.2f} DNY, Komisi: {details['Commission']:.2f} DNY, Base Reward: {details['Base Reward']:.2f} DNY")
            self.draw_graph()
        else:
            with self.output_area:
                clear_output(wait=True)
                print("Masukkan jumlah hari yang valid.")



# Membuat instance dari MLMSystemInteractive dan menampilkan antarmuka
mlm_interactive = MLMSystemInteractive()
