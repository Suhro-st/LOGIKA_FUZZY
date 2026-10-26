# ==========================================================
# 1. KELAS STRUKTUR ATURAN FUZZY
# ==========================================================
class FuzzyRule:
    def __init__(self, rule_id, antecedent, consequent, operator='AND'):
        """
        antecedent: dict berisi pasangan {'nama_variabel': 'nama_label'}
                    contoh: {'waktu': 'Sedang', 'urgensi': 'Tinggi'}
        consequent: dict berisi {'nama_variabel': 'nama_label'}
                    contoh: {'prioritas': 'Tinggi'}
        """
        self.rule_id = rule_id
        self.antecedent = antecedent
        self.consequent = consequent
        self.operator = operator.upper()

    def hitung_firing_strength(self, derajat_fuzzifikasi):
        """
        derajat_fuzzifikasi: dict bersarang berisi derajat keanggotaan input,
        contoh: {'waktu': {'Cepat': 0.0, 'Sedang': 0.4, 'Lama': 0.6},
                 'urgensi': {'Rendah': 0.0, 'Sedang': 0.7, 'Tinggi': 0.3}}
        """
        nilai_derajat = []
        for var_nama, label_nama in self.antecedent.items():
            deg = derajat_fuzzifikasi[var_nama].get(label_nama, 0.0)
            nilai_derajat.append(deg)

        if not nilai_derajat:
            return 0.0

        if self.operator == 'AND':
            return min(nilai_derajat)
        elif self.operator == 'OR':
            return max(nilai_derajat)
        else:
            raise ValueError(f"Operator {self.operator} tidak dikenali.")

    def __str__(self):
        syarat = f" {self.operator} ".join([f"{var} is {lbl}" for var, lbl in self.antecedent.items()])
        hasil = ", ".join([f"{var} is {lbl}" for var, lbl in self.consequent.items()])
        return f"[{self.rule_id}] IF {syarat} THEN {hasil}"


# ==========================================================
# 2. INISIALISASI BASIS ATURAN (RULE BASE)
# ==========================================================
rule_base = [
    FuzzyRule("R1", {"waktu": "Cepat", "urgensi": "Rendah"}, {"prioritas": "Rendah"}),
    FuzzyRule("R2", {"waktu": "Cepat", "urgensi": "Sedang"}, {"prioritas": "Rendah"}),
    FuzzyRule("R3", {"waktu": "Cepat", "urgensi": "Tinggi"}, {"prioritas": "Sedang"}),
    FuzzyRule("R4", {"waktu": "Sedang", "urgensi": "Rendah"}, {"prioritas": "Rendah"}),
    FuzzyRule("R5", {"waktu": "Sedang", "urgensi": "Sedang"}, {"prioritas": "Sedang"}),
    FuzzyRule("R6", {"waktu": "Sedang", "urgensi": "Tinggi"}, {"prioritas": "Tinggi"}),
    FuzzyRule("R7", {"waktu": "Lama", "urgensi": "Rendah"}, {"prioritas": "Sedang"}),
    FuzzyRule("R8", {"waktu": "Lama", "urgensi": "Sedang"}, {"prioritas": "Tinggi"}),
    FuzzyRule("R9", {"waktu": "Lama", "urgensi": "Tinggi"}, {"prioritas": "Kritis"}),
]


# ==========================================================
# 3. EVALUASI ATURAN TERHADAP DATA INPUT
# ==========================================================
derajat_input_sampel = {
    "waktu": {"Cepat": 0.0, "Sedang": 0.4, "Lama": 0.6},
    "urgensi": {"Rendah": 0.0, "Sedang": 0.7, "Tinggi": 0.3}
}

print("=" * 75)
print("HASIL EVALUASI BASIS ATURAN FUZZY")
print("=" * 75)

aturan_aktif = []
for rule in rule_base:
    alpha = rule.hitung_firing_strength(derajat_input_sampel)
    output_var = list(rule.consequent.keys())[0]
    output_lbl = rule.consequent[output_var]
    status = f"AKTIF (alpha = {alpha:.2f})" if alpha > 0 else "NONAKTIF"
    print(f"{rule} --> {status}")
    if alpha > 0:
        aturan_aktif.append((rule.rule_id, output_lbl, alpha))

print("\n" + "=" * 75)
print("RINGKASAN ATURAN YANG TEPICU (FIRING RULES):")
print("=" * 75)
for r_id, konklusi, alpha in aturan_aktif:
    print(f" - {r_id:<4} : Prioritas = {konklusi:<8} dengan alpha = {alpha:.2f}")
