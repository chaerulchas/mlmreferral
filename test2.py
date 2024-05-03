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
        self.commissions = {}
        self.days = 0

    def add_user(self, user_id, user_name, staking_amount, referrer=None):
        """Menambahkan pengguna baru dengan nama, jumlah staking, dan referrer."""
        self.users[user_id] = {
            'name': user_name,
            'staking': staking_amount,
            'base_reward': 0,
            'commission': 0,
            'total_reward': 0
        }
        if referrer:
            if referrer in self.referrals:
                self.referrals[referrer].append(user_id)
            else:
                self.referrals[referrer] = [user_id]

    def calculate_rewards(self, days):
        """Menghitung rewards, komisi, dan royalti untuk semua pengguna."""
        for user, details in self.users.items():
            details['base_reward'] = details['staking'] * 0.12 / 365 * days  # 12% dari staking per tahun

        # Reset komisi setiap kali fungsi ini dipanggil
        self.commissions = {}

        for referrer, referrals in self.referrals.items():
            for level, referral in enumerate(referrals):
                self.calculate_commission_and_royalty(referrer, referral, 1)  # Mulai dari level 1

        # Setelah menghitung semua komisi, perbarui total reward
        for user, details in self.users.items():
            details['total_reward'] = details['base_reward'] - details['commission']

    def calculate_commission_and_royalty(self, referrer, referral, level):
        """Rekursif menghitung komisi dan royalti hingga 4 level."""
        if level > 4:
            return  # Batasi hingga 4 level, level 4 tidak menerima apa-apa

        referral_reward = self.users[referral]['base_reward']
        commission_rate = [0.05, 0.03, 0.02, 0][level - 1]  # Tarif komisi untuk setiap level
        commission = referral_reward * commission_rate

        # Rekam komisi untuk setiap referrer dan referral
        self.users[referrer]['commission'] += commission
        if referrer not in self.commissions:
            self.commissions[referrer] = {}
        self.commissions[referrer][referral] = commission

        # Lanjutkan ke parent referrer jika belum mencapai level 4
        parent_referrer = next((key for key, value in self.referrals.items() if referrer in value), None)
        if parent_referrer:
            self.calculate_commission_and_royalty(parent_referrer, referral, level + 1)

    def get_commission_report(self):
        return {user: {'Stake': details['staking'], 'Total Reward': details['total_reward'], 'Commission': details['commission']} for user, details in self.users.items()}

class MLMSystemInteractive(MLMSystem):
    def __init__(self):
        super().__init__()
        self.output_area = widgets.Output()
        self.graph_area = widgets.Output()
        self.create_widgets()

    def create_widgets(self):
        self.user_id_input = widgets.Text(description="User ID:")
        self.user_name_input = widgets.Text(description="Nama User:")
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
        with self.graph_area:
            clear_output(wait=True)
            G = nx.DiGraph()
            for referrer, referrals in self.referrals.items():
                for referral in referrals:
                    referrer_data = self.users[referrer]
                    referral_data = self.users[referral]
                    referrer_label = f"{referrer_data['name']} ({referrer})\nStaking: {referrer_data['staking']}\nReward: {referrer_data['total_reward']:.2f}\nKomisi: {referrer_data['commission']:.2f}"
                    referral_label = f"{referral_data['name']} ({referral})\nStaking: {referral_data['staking']}\nReward: {referral_data['total_reward']:.2f}\nKomisi: {referral_data['commission']:.2f}"
                    
                    commission_label = f"Comm: {self.commissions[referrer].get(referral, 0):.2f}" if referrer in self.commissions and referral in self.commissions[referrer] else "Comm: 0.00"
                    G.add_edge(referrer_label, referral_label, label=commission_label)

            pos = nx.spring_layout(G)
            plt.figure(figsize=(12, 8))
            edges = G.edges(data=True)
            nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=3500, alpha=0.6)
            nx.draw_networkx_edges(G, pos, edgelist=edges, arrowstyle='-|>', arrowsize=10)
            nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
            edge_labels = { (u, v): d['label'] for u, v, d in edges }
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='blue')
            plt.title('Jaringan Referral')
            plt.axis('off')
            plt.show()

    def add_user_action(self, b):
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
                print("Masukkan detail pengguna yang valid.")

    def calculate_rewards_action(self, b):
        days_spent = self.days_spent.value
        if days_spent > 0:
            self.calculate_rewards(days_spent)
            commission_report = self.get_commission_report()
            with self.output_area:
                clear_output(wait=True)
                print(f"Laporan Komisi setelah {self.days} hari:")
                for user, details in commission_report.items():
                    print(f"{user}: Stake: ${details['Stake']:.2f}, Total Reward: ${details['Total Reward']:.2f}, Komisi: ${details['Commission']:.2f}")
            self.draw_graph()
        else:
            with self.output_area:
                clear_output(wait=True)
                print("Masukkan jumlah hari yang valid.")

# Membuat instance dari MLMSystemInteractive dan menampilkan antarmuka
mlm_interactive = MLMSystemInteractive()
