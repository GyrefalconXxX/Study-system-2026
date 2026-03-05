import json
import os
import time
import sys
from datetime import datetime, date
import msvcrt  # Windows-specific keyboard input

# --- CONFIGURATION ---
GRIT_FILE = "progress.json"
CHECKLIST_FILE = "checklist.json"
PAPER_FILE = "papers.json"
THEORY_FILE = "theory.json"

MODULE_MAX = {
    "P1": 75, "P2": 75, "P3": 75, "P4": 75,
    "S1": 75, "S2": 75,
    "B4": 90, "B5": 90, "B6": 50,
    "C4": 90, "C5": 90, "C6": 50
}

SYLLABUS = {
    "P4": [
        ("CH1 PROOF", "Proof by Contradiction"),
        ("CH2 PARTIAL FRACTIONS", "Partial Fractions"),
        ("CH2 PARTIAL FRACTIONS", "Repeated Factors"),
        ("CH2 PARTIAL FRACTIONS", "Improper Fractions"),
        ("CH3 COORD GEOMETRY", "Parametric Equations"),
        ("CH3 COORD GEOMETRY", "Using Trigonometric Identities"),
        ("CH3 COORD GEOMETRY", "Curve Sketching"),
        ("CH4 BINOMIAL", "Expanding (1 + x)^n"),
        ("CH4 BINOMIAL", "Expanding (a + bx)^n"),
        ("CH4 BINOMIAL", "Using Partial Fractions"),
        ("CH5 DIFFERENTIATION", "Parametric Differentiation"),
        ("CH5 DIFFERENTIATION", "Implicit Differentiation"),
        ("CH5 DIFFERENTIATION", "Rates of Change"),
        ("CH6 INTEGRATION", "Area Under Curves (Parametric)"),
        ("CH6 INTEGRATION", "Volumes of Revolution (x-axis)"),
        ("CH6 INTEGRATION", "Integration by Substitution"),
        ("CH6 INTEGRATION", "Integration by Parts"),
        ("CH6 INTEGRATION", "Integration Using Partial Fractions"),
        ("CH6 INTEGRATION", "Solving Differential Equations"),
        ("CH6 INTEGRATION", "Modelling with Differential Equations"),
        ("CH7 VECTORS", "Representing Vectors"),
        ("CH7 VECTORS", "Magnitude and Direction"),
        ("CH7 VECTORS", "Vectors in 3D"),
        ("CH7 VECTORS", "Geometric Problems (2D)"),
        ("CH7 VECTORS", "Geometric Problems (3D)"),
        ("CH7 VECTORS", "Position Vectors"),
        ("CH7 VECTORS", "3D Coordinates"),
        ("CH7 VECTORS", "Equation of a Line (3D)"),
        ("CH7 VECTORS", "Points of Intersection"),
        ("CH7 VECTORS", "The Scalar Product")
    ],
    "S2": [
        ("CH1 BINOMIAL", "The Binomial Distribution"),
        ("CH1 BINOMIAL", "Cumulative Probabilities"),
        ("CH1 BINOMIAL", "Mean and Variance of Binomial"),
        ("CH2 POISSON", "The Poisson Distribution"),
        ("CH2 POISSON", "Modelling with Poisson"),
        ("CH2 POISSON", "Adding Poisson Distributions"),
        ("CH2 POISSON", "Mean and Variance of Poisson"),
        ("CH3 APPROX", "Poisson to Approx Binomial"),
        ("CH3 APPROX", "Binomial to Normal Approx"),
        ("CH3 APPROX", "Poisson to Normal Approx"),
        ("CH3 APPROX", "Choosing Appropriate Approx"),
        ("CH4 CRVs", "Continuous Random Variables"),
        ("CH4 CRVs", "The Cumulative Distribution Function"),
        ("CH4 CRVs", "Mean and Variance of Continuous Dist"),
        ("CH4 CRVs", "Mode, Median, Quartiles, Percentiles"),
        ("CH5 UNIFORM", "The Continuous Uniform Distribution"),
        ("CH5 UNIFORM", "Modelling with Uniform Dist"),
        ("CH6 SAMPLING", "Populations and Samples"),
        ("CH6 SAMPLING", "The Concept of a Statistic"),
        ("CH6 SAMPLING", "The Sampling Distribution of a Statistic"),
        ("CH7 HYPOTHESIS", "Hypothesis Testing Principles"),
        ("CH7 HYPOTHESIS", "Finding Critical Values"),
        ("CH7 HYPOTHESIS", "One-tailed Tests"),
        ("CH7 HYPOTHESIS", "Two-tailed Tests"),
        ("CH7 HYPOTHESIS", "Testing Mean Lambda of Poisson"),
        ("CH7 HYPOTHESIS", "Using Approximations in Testing")
    ]
}

class GritSystem:
    def __init__(self):
        self.multiplier = 0.05
        self.data = self.load_grit_data()
        self.checklist = self.load_checklist_data()
        self.papers = self.load_paper_data()
        self.theory = self.load_theory_data()

    def load_grit_data(self):
        if os.path.exists(GRIT_FILE):
            with open(GRIT_FILE, 'r') as f:
                d = json.load(f)
                if "streak" not in d: d["streak"] = 0
                if "last_xp_date" not in d: d["last_xp_date"] = None
                return d
        return {"xp_towards_level": 0, "balance": 0, "level": 1, "history": [], "streak": 0, "last_xp_date": None}

    def load_checklist_data(self):
        if os.path.exists(CHECKLIST_FILE):
            with open(CHECKLIST_FILE, 'r') as f: return json.load(f)
        return {"active": [], "completed": [], "deleted": []}

    def load_paper_data(self):
        if os.path.exists(PAPER_FILE):
            with open(PAPER_FILE, 'r') as f: return json.load(f)
        return []

    def load_theory_data(self):
        if os.path.exists(THEORY_FILE):
            with open(THEORY_FILE, 'r') as f: return json.load(f)
        # Create fresh state from syllabus
        fresh_theory = {}
        for sub, topics in SYLLABUS.items():
            fresh_theory[sub] = [{"ch": t[0], "topic": t[1], "done": False} for t in topics]
        return fresh_theory

    def save_all(self):
        with open(GRIT_FILE, 'w') as f: json.dump(self.data, f, indent=4)
        with open(CHECKLIST_FILE, 'w') as f: json.dump(self.checklist, f, indent=4)
        with open(PAPER_FILE, 'w') as f: json.dump(self.papers, f, indent=4)
        with open(THEORY_FILE, 'w') as f: json.dump(self.theory, f, indent=4)

    def log_event(self, entry):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.data["history"].append(f"[{timestamp}] {entry}")
        if len(self.data["history"]) > 30: self.data["history"].pop(0)

    def update_streak(self):
        today = str(date.today())
        last_date_str = self.data["last_xp_date"]
        if last_date_str == today: return
        if last_date_str:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            delta = (date.today() - last_date).days
            if delta == 1: self.data["streak"] += 1
            elif delta > 1: self.data["streak"] = 1
        else: self.data["streak"] = 1
        self.data["last_xp_date"] = today
        self.save_all()

    def add_xp(self, amount, source):
        amount = round(amount, 2)
        if amount > 0: self.update_streak()
        self.data["xp_towards_level"] += amount
        self.data["balance"] += amount
        self.log_event(f"+{amount} XP ({source})")
        while self.data["xp_towards_level"] >= (self.data["level"] * 200):
            self.data["xp_towards_level"] -= (self.data["level"] * 200)
            self.data["level"] += 1
            print(f"\n🎊 LEVEL UP! Reached Level {self.data['level']}!")
        self.save_all()

    def fix_mistake(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🔧 --- XP MAINTENANCE ---")
        print(f"Current Balance: {self.data['balance']:.2f} XP")
        try:
            to_remove = float(input("\nHow much XP to subtract?: "))
            if to_remove > 0:
                self.data["balance"] = max(0, self.data["balance"] - to_remove)
                self.data["xp_towards_level"] = max(0, self.data["xp_towards_level"] - to_remove)
                self.log_event(f"REMOVED {to_remove} XP (Correction)")
                self.save_all()
                print(f"\n✅ Adjusted! Deducted {to_remove} XP.")
        except: print("\n❌ Invalid input.")
        input("\nPress Enter...")

    def generate_body_reset_guide(self):
        guide = """--- THE BODY RESET GUIDE ---
1. FORWARD FOLD: Stand or sit, hang head/torso over knees. 
   Breathe into lower back. (Decompresses spine)

2. WALL CHEST STRETCH: Arm against doorframe, turn away. 
   (Opens up chest from writing hunch)

3. THE SPHINX: Lie on belly, prop on elbows, look forward. 
   (Counters looking down at papers)

4. BELLY BREATHING: 5 mins slow breathing. 
   (Lowers cortisol, helps fasting/sleep)"""
        with open("body_reset_guide.txt", "w") as f:
            f.write(guide)

    def spend_xp(self, amount, item):
        if self.data["balance"] >= amount:
            self.data["balance"] -= amount
            self.log_event(f"Spent {amount} XP on {item}")
            print(f"\n🛍️ PURCHASED: {item}")
            if item == "Body Reset":
                self.generate_body_reset_guide()
                print("📖 Guide generated: body_reset_guide.txt")
                os.startfile("body_reset_guide.txt") if os.name == 'nt' else None
        else:
            print(f"\n❌ NEED {amount - self.data['balance']:.2f} MORE XP.")
        self.save_all()

    # --- EXAM HALL ---
    def log_paper(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("📝 --- NEW PAPER LOG ---")
        code = input("Paper Code (e.g., S1M23): ").strip().upper()
        module = code[:2]
        if module not in MODULE_MAX:
            print(f"❌ Unknown module '{module}'."); time.sleep(1); return
        
        try:
            is_tuition = input("Is this a TUITION/CLASS paper? (y/n): ").lower() == 'y'
            log_date = input("Date (e.g., Feb15): ").strip()
            
            if is_tuition:
                print("\n--- 🎓 TUITION MODE ---")
                total_q = int(input("Total Questions (inc. parts): "))
                my_ans = int(input("My Answers (Black Ink): "))
                if total_q == 0: total_q = 1
                perc = round((my_ans / total_q) * 100, 1)
                xp_earned = round((perc / 100) * 150, 2)
                paper_entry = {
                    "date": log_date, "code": code, "module": module,
                    "marks": my_ans, "max": total_q,
                    "timed": False, "xp": xp_earned, "perc": perc,
                    "is_tuition": True
                }
                print(f"\n" + "-"*35)
                print(f"PREVIEW: {log_date} | {code} [TUI] | Indep: {perc}% ({my_ans}/{total_q})")
                print(f"REWARD: {xp_earned} XP (Based on Effort)")
            else:
                marks = float(input(f"Marks Gained (Max {MODULE_MAX[module]}): "))
                is_timed = input("Timed? (y/n): ").lower() == 'y'
                mult = 1.15 if is_timed else 1.0
                xp_earned = round(marks * mult, 2)
                perc = round((marks / MODULE_MAX[module]) * 100, 1)
                paper_entry = {
                    "date": log_date, "code": code, "module": module, 
                    "marks": marks, "max": MODULE_MAX[module], 
                    "timed": is_timed, "xp": xp_earned, "perc": perc,
                    "is_tuition": False
                }
                t_lbl = "T" if is_timed else "-"
                print(f"\n" + "-"*35)
                print(f"PREVIEW: {log_date} | {code} | {marks}/{MODULE_MAX[module]} ({perc}%) | [{t_lbl}]")
                print(f"REWARD: {xp_earned} XP")

            print("-" * 35)
            if input("Confirm entry? (Enter/y): ").lower() in ['', 'y']:
                self.papers.append(paper_entry)
                # Sort papers by module grouping then code
                self.papers.sort(key=lambda x: (x["module"], x["code"]))
                source_lbl = f"Tuition Paper {code}" if is_tuition else f"Completed Paper {code}"
                self.add_xp(xp_earned, source_lbl)
                print("✅ Paper archived!")
        except Exception as e: print(f"❌ Error: {e}")
        input("\nPress Enter...")

    def view_paper_table(self, pause=True):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n" + "═"*130)
        print(f"{'#':<3} | {'DATE':<12} | {'CODE':<15} | {'MODULE':<10} | {'SCORE/INDEP':<15} | {'%':<10} | {'TYPE':<10} | {'XP'}")
        print("─"*130)
        for i, p in enumerate(self.papers):
            is_tui = p.get("is_tuition", False) 
            if is_tui:
                t_lbl = "[TUI]"
                score_disp = f"{int(p['marks'])}/{int(p['max'])}"
            else:
                t_lbl = "T" if p["timed"] else "-"
                score_disp = f"{p['marks']}/{p['max']}"
            print(f"{i+1:<3} | {p['date']:<12} | {p['code']:<15} | {p['module']:<10} | {score_disp:<15} | {p['perc']:<10} | {t_lbl:<10} | {p['xp']:.2f}")
        print("═"*130)
        if pause: input("\nPress Enter...")

    def delete_paper(self):
        self.view_paper_table(pause=False)
        try:
            idx = int(input("\nEnter Paper # to Delete (0 to cancel): ")) - 1
            if idx >= 0:
                removed = self.papers.pop(idx)
                self.save_all()
                print(f"🗑️ Removed {removed['code']}")
        except: print("❌ Invalid selection.")
        input("\nPress Enter...")

    def view_analytics(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("📊 --- MODULE ANALYTICS ---")
        modules = sorted(list(set(p["module"] for p in self.papers)))
        if not modules: print("\n(No papers logged yet)")
        for mod in modules:
            t_scores = [p["perc"] for p in self.papers if p["module"] == mod and p.get("timed") and not p.get("is_tuition")]
            u_scores = [p["perc"] for p in self.papers if p["module"] == mod and not p.get("timed") and not p.get("is_tuition")]
            tui_count = len([p for p in self.papers if p["module"] == mod and p.get("is_tuition")])
            print(f"\n{mod}:")
            if t_scores: print(f"  Timed Mean:   {sum(t_scores)/len(t_scores):.1f}% ({len(t_scores)} papers)")
            if u_scores: print(f"  Untimed Mean: {sum(u_scores)/len(u_scores):.1f}% ({len(u_scores)} papers)")
            if tui_count > 0: print(f"  Tuition Done: {tui_count} papers (Not included in mean)")
        input("\nPress Enter...")

    def start_the_grind(self):
        task_str = ""
        if not self.checklist["active"]:
            task_str = "      (No active tasks)\n"
        else:
            for i, item in enumerate(self.checklist["active"]):
                symbol = "[ ]" if item["status"] == "undone" else "[🚧]"
                task_str += f"      {i+1}. {symbol} {item['task']}\n\n"
        os.system('cls' if os.name == 'nt' else 'clear')
        # Clear buffer
        while msvcrt.kbhit(): msvcrt.getch()
        start_time = time.time()
        while True:
            sys.stdout.write("\033[H")
            cur_dur = int(time.time() - start_time)
            cur_xp = cur_dur * self.multiplier
            prog = min(cur_xp / 50.0, 1.0)
            bar = "█" * int(40 * prog) + "-" * (40 - int(40 * prog))
            hud = (
                f"\n      " + "🔥" * 5 + " THE GRIND IS ACTIVE " + "🔥" * 5 + "\n"
                f"\n      ⏱️  TIMER: {cur_dur//60:02d}:{cur_dur%60:02d}"
                f"\n      💎 XP: {cur_xp:.2f} / 50.00"
                f"\n      [{bar}] {prog*100:>5.1f}%\n"
                f"\n      " + "─" * 45 + "\n"
                f"      📜 CURRENT OBJECTIVES:\n\n"
                f"{task_str}"
                f"      " + "─" * 45 + "\n"
                f"\n      >> Press ANY KEY to finish and bank XP <<"
            )
            sys.stdout.write(hud); sys.stdout.flush()
            if msvcrt.kbhit():
                msvcrt.getch()
                break
            time.sleep(0.1)
        final_xp = (time.time() - start_time) * self.multiplier
        self.add_xp(final_xp, "Grind Session")
        input("\n\nSession Complete! Press Enter...")

    def print_active_tasks(self):
        if not self.checklist["active"]:
            print("  (No active tasks)"); return
        for i, item in enumerate(self.checklist["active"]):
            symbol = "[ ]" if item["status"] == "undone" else "[🚧]"
            print(f"  {i+1}. {symbol} {item['task']}\n")

    def checklist_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear') 
            print("\n" + "="*55 + " 📝 CHECKLIST " + "="*55)
            self.print_active_tasks()
            print("-" * 130)
            print("1. Add | 2. Toggle | 3. Delete | 4. Archives | 5. BULK PASTE | 6. Back")
            c = input("\nAction: ")
            if c == "1":
                t = input("Task: "); self.checklist["active"].append({"task": t, "status": "undone"}); self.save_all()
            elif c == "2":
                try:
                    idx = int(input("Task #: ")) - 1
                    item = self.checklist["active"][idx]
                    if item["status"] == "undone": item["status"] = "progressing"
                    else: self.checklist["completed"].append(self.checklist["active"].pop(idx))
                    self.save_all()
                except: pass
            elif c == "3":
                try:
                    idx = int(input("Delete #: ")) - 1
                    self.checklist["deleted"].append(self.checklist["active"].pop(idx)); self.save_all()
                except: pass
            elif c == "4": self.archive_menu()
            elif c == "5": self.paste_tasks()
            elif c == "6": break

    def archive_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n--- ARCHIVES ---")
            for i, item in enumerate(self.checklist["completed"]): 
                print(f"  C{i+1}. [✔] {item['task']}")
            for i, item in enumerate(self.checklist["deleted"]): 
                print(f"  D{i+1}. [🗑] {item['task']}")
            
            print("\n" + "-"*30)
            print("Commands: Type code to Revive (e.g., 'D1' or 'C2') | 'b' to Back")
            cmd = input("\nAction: ").strip().upper()
            
            if cmd == 'B': break
            
            try:
                # Determine which list to pull from
                if cmd.startswith('D'):
                    idx = int(cmd[1:]) - 1
                    item = self.checklist["deleted"].pop(idx)
                elif cmd.startswith('C'):
                    idx = int(cmd[1:]) - 1
                    item = self.checklist["completed"].pop(idx)
                else:
                    continue
                
                # Reset and move back to active
                item["status"] = "undone"
                self.checklist["active"].append(item)
                self.save_all() # Crucial: Save the move!
                print(f"♻️  Restored: {item['task']}"); time.sleep(0.5)
            except:
                print("❌ Invalid code."); time.sleep(0.5)
                
    def paste_tasks(self):
        print("\nBULK PASTE: Type tasks then 'DONE'.")
        new = []
        while True:
            line = input()
            if line.strip().upper() == "DONE": break
            if line.strip(): new.append(line.strip())
        for t in new: self.checklist["active"].append({"task": t, "status": "undone"})
        self.save_all()

    # --- NEW THEORY MASTERY TRACKER ---
    def theory_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("📖 --- THEORY MASTERY TRACKER ---")
            for sub in ["P4", "S2"]:
                done = len([t for t in self.theory[sub] if t["done"]])
                total = len(self.theory[sub])
                perc = (done/total)*100
                bar = "█" * int(perc/5) + "░" * (20 - int(perc/5))
                print(f" {sub} Mastery: [{bar}] {perc:.1f}%")
            print("\n1. P4 Theory | 2. S2 Theory | 3. Back")
            choice = input("\nSelect: ")
            if choice == "1": self.subject_theory_menu("P4")
            elif choice == "2": self.subject_theory_menu("S2")
            elif choice == "3": break

    def subject_theory_menu(self, sub):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"📗 --- {sub} THEORY LIST ---")
            current_ch = ""
            for i, t in enumerate(self.theory[sub]):
                if t["ch"] != current_ch:
                    current_ch = t["ch"]
                    print(f"\n--- {current_ch} ---")
                status = "⭐" if t["done"] else "  "
                print(f" {i+1}. {status} {t['topic']}\n")
            print("-" * 50)
            print("Commands: [Number] to Toggle | 'b' to Back")
            cmd = input("\nAction: ").lower().strip()
            if cmd == 'b': break
            else:
                try:
                    idx = int(cmd) - 1
                    topic = self.theory[sub][idx]
                    topic["done"] = not topic["done"]
                    if topic["done"]: self.add_xp(15, f"Mastered {sub}: {topic['topic']}")
                    self.save_all()
                except: pass

def main():
    gs = GritSystem()
    os.system("title The Grit Engine v13.5")
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n" + "═"*130)
        print(f" GRIT-WALKER LVL: {gs.data['level']} | BAL: {gs.data['balance']:.2f} XP | 🔥 STREAK: {gs.data['streak']} DAYS")
        print("─"*130)
        print(" 📝 ACTIVE TASKS:\n")
        gs.print_active_tasks()
        print("═"*130)
        print("1. START THE GRIND | 2. THE EXAM HALL | 3. THEORY TRACKER | 4. REWARD SHOP | 5. HISTORY | 6. CHECKLIST | 7. MAINTENANCE | 8. EXIT")
        cmd = input("\nAction: ")
        if cmd == "1": gs.start_the_grind()
        elif cmd == "2":
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("🏛️ --- THE EXAM HALL ---")
                print("1. Log Paper | 2. View Table | 3. View Analytics | 4. Delete Entry | 5. Back")
                sub = input("\nChoice: ")
                if sub == "1": gs.log_paper()
                elif sub == "2": gs.view_paper_table()
                elif sub == "3": gs.view_analytics()
                elif sub == "4": gs.delete_paper()
                elif sub == "5": break
        elif cmd == "3": gs.theory_menu()
        elif cmd == "4":
            print("\n1. Signature Mocha (100) | 2. Writing Session (80)")
            print("3. Scented Candle Ritual (50) | 4. Body Reset (40) | 5. Literature Dive (120)")
            c = input("\nClaim: ")
            if c == "1": gs.spend_xp(100, "Mocha")
            elif c == "2": gs.spend_xp(80, "Writing Session")
            elif c == "3": gs.spend_xp(50, "Scented Candle")
            elif c == "4": gs.spend_xp(40, "Body Reset")
            elif c == "5": gs.spend_xp(120, "Literature Dive")
            input("Enter...")
        elif cmd == "5":
            print("\nQuest Log:"); [print(l) for l in gs.data["history"]]; input("\nEnter...")
        elif cmd == "6": gs.checklist_menu()
        elif cmd == "7": gs.fix_mistake()
        elif cmd == "8": break

if __name__ == "__main__": main()