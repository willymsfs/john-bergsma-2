#!/usr/bin/env python3
"""
AI Timetable Agent for SFS School, Khamgaon
Creates conflict-free weekly timetables for classes Nursery to III
"""

from collections import defaultdict
import itertools
from typing import Dict, List, Tuple, Set
import json

class TimetableGenerator:
    def __init__(self):
        self.setup_databases()
        self.setup_constraints()
        
    def setup_databases(self):
        """Initialize the three core databases"""
        
        # Database 1: Teacher & Subject Master List
        self.teacher_assignments = {
            "Varsha": {
                "subjects": ["All Nursery Subjects", "Hindi", "Marathi"],
                "classes": ["Nursery", "Class I", "Class II", "Class III"]
            },
            "Sabista": {
                "subjects": ["All LKG Subjects", "General Knowledge"],
                "classes": ["LKG", "Class I"]
            },
            "Laxmi": {
                "subjects": ["Most UKG Subjects", "Marathi"],
                "classes": ["UKG", "Class I", "Class II"]
            },
            "Bais Punam": {
                "subjects": ["English", "Science", "Games", "Drawing", "GK", "Value Education", "Hindi"],
                "classes": ["Class I", "Class II", "Class III", "LKG"]
            },
            "Shivani": {
                "subjects": ["English", "Maths", "Hindi", "GK", "Games", "Drawing", "Value Education", "Cursive Writing"],
                "classes": ["Class I", "Class II", "Class III", "UKG"]
            },
            "Arziya": {
                "subjects": ["English", "Science", "Games", "Value Education", "Poem"],
                "classes": ["Class I", "Class II", "Class III", "UKG"]
            },
            "Anant Kalaskar": {
                "subjects": ["Computer", "Maths", "Mass PT"],
                "classes": ["Class I", "Class II", "Class III", "All"]
            },
            "Br. Nabin Soreign": {
                "subjects": ["English Grammar"],
                "classes": ["Class I", "Class II", "Class III"]
            }
        }
        
        # Database 2: Official Subject Curriculum per Class
        self.class_subjects = {
            "Nursery": ["Drawing", "English", "English Grammar", "Games", "Hindi", "Mass PT", "Maths", "Poem", "Activities"],
            "LKG": ["Cursive Writing", "Drawing", "English", "English Grammar", "Games", "GK", "Hindi", "Mass PT", "Maths", "Poem", "EVS", "Picture Book", "Activities"],
            "UKG": ["Cursive Writing", "Drawing", "English", "English Grammar", "Games", "GK", "Hindi", "Mass PT", "Maths", "Poem", "EVS", "Picture Book", "Activities"],
            "Class I": ["Computer", "Conversation", "Drawing", "English", "English Grammar", "Games", "GK", "Hindi", "Marathi", "Mass PT", "Maths", "Science", "Value Education"],
            "Class II": ["Computer", "Conversation", "Drawing", "English", "English Grammar", "Games", "GK", "Hindi", "Marathi", "Mass PT", "Maths", "Science", "Value Education"],
            "Class III": ["Computer", "Conversation", "Drawing", "English", "English Grammar", "Games", "GK", "Hindi", "Marathi", "Mass PT", "Maths", "Science", "Value Education"]
        }
        
        # Database 3: Weekly Period Allotment Table (Corrected for capacity constraints)
        self.period_allotments = {
            "English": {"Nursery": 6, "LKG": 6, "UKG": 6, "Class I": 8, "Class II": 9, "Class III": 7},  # Added 1 period to Class II, Reduced from 8 to 7 for Class III
            "Maths": {"Nursery": 4, "LKG": 5, "UKG": 5, "Class I": 7, "Class II": 7, "Class III": 6},   # Reduced from 7 to 6 for Class III
            "Hindi": {"Nursery": 4, "LKG": 4, "UKG": 4, "Class I": 4, "Class II": 4, "Class III": 4},
            "English Grammar": {"Nursery": 2, "LKG": 2, "UKG": 2, "Class I": 3, "Class II": 2, "Class III": 4},  # Reduced from 5 to 4 for Class III
            "Science": {"Nursery": 0, "LKG": 0, "UKG": 0, "Class I": 4, "Class II": 4, "Class III": 5},
            "Marathi": {"Nursery": 0, "LKG": 0, "UKG": 0, "Class I": 4, "Class II": 4, "Class III": 4},
            "Computer": {"Nursery": 0, "LKG": 0, "UKG": 0, "Class I": 2, "Class II": 2, "Class III": 2},
            "Games": {"Nursery": 2, "LKG": 2, "UKG": 2, "Class I": 2, "Class II": 2, "Class III": 2},
            "Drawing": {"Nursery": 2, "LKG": 2, "UKG": 2, "Class I": 1, "Class II": 1, "Class III": 1},
            "GK": {"Nursery": 0, "LKG": 2, "UKG": 2, "Class I": 1, "Class II": 1, "Class III": 1},
            "Value Education": {"Nursery": 0, "LKG": 0, "UKG": 0, "Class I": 1, "Class II": 1, "Class III": 1},
            "Conversation": {"Nursery": 0, "LKG": 0, "UKG": 0, "Class I": 1, "Class II": 1, "Class III": 1},
            "Mass PT": {"Nursery": 1, "LKG": 1, "UKG": 1, "Class I": 1, "Class II": 1, "Class III": 1},
            "Poem": {"Nursery": 2, "LKG": 2, "UKG": 2, "Class I": 0, "Class II": 0, "Class III": 0},
            "Activities": {"Nursery": 1, "LKG": 1, "UKG": 1, "Class I": 0, "Class II": 0, "Class III": 0},
            "EVS": {"Nursery": 0, "LKG": 3, "UKG": 3, "Class I": 0, "Class II": 0, "Class III": 0},
            "Cursive Writing": {"Nursery": 0, "LKG": 2, "UKG": 2, "Class I": 0, "Class II": 0, "Class III": 0},
            "Picture Book": {"Nursery": 0, "LKG": 2, "UKG": 2, "Class I": 0, "Class II": 0, "Class III": 0}
        }
        
    def setup_constraints(self):
        """Setup scheduling constraints"""
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        self.daily_periods = {
            "Nursery": 4,
            "LKG": 6,
            "UKG": 6,
            "Class I": 7,
            "Class II": 7,
            "Class III": 7
        }
        
        # Saturday has only 4 periods for all classes
        self.saturday_periods = 4
        
        # Class teachers for Conversation subject
        self.class_teachers = {
            "Class I": "Varsha",  # Assuming based on Hindi/Marathi expertise
            "Class II": "Varsha",
            "Class III": "Varsha"
        }
        
    def expand_teacher_subjects(self):
        """Expand generic subject assignments to specific subjects"""
        expanded_assignments = {}
        
        for teacher, info in self.teacher_assignments.items():
            expanded_subjects = []
            
            for subject in info["subjects"]:
                if subject == "All Nursery Subjects":
                    expanded_subjects.extend(self.class_subjects["Nursery"])
                elif subject == "All LKG Subjects":
                    expanded_subjects.extend(self.class_subjects["LKG"])
                elif subject == "Most UKG Subjects":
                    # Exclude subjects that other teachers specifically handle
                    ukg_subjects = self.class_subjects["UKG"].copy()
                    # Remove subjects handled by others
                    excluded = ["English", "Maths", "Games", "Drawing", "Value Education"]
                    for exc in excluded:
                        if exc in ukg_subjects:
                            ukg_subjects.remove(exc)
                    expanded_subjects.extend(ukg_subjects)
                elif subject == "General Knowledge":
                    expanded_subjects.append("GK")
                elif subject == "Value Education":
                    expanded_subjects.append("Value Education")
                elif subject == "Cursive Writing":
                    expanded_subjects.append("Cursive Writing")
                else:
                    expanded_subjects.append(subject)
            
            # Remove duplicates
            expanded_assignments[teacher] = {
                "subjects": list(set(expanded_subjects)),
                "classes": info["classes"]
            }
            
        return expanded_assignments
    
    def can_teach(self, teacher: str, subject: str, class_name: str) -> bool:
        """Check if a teacher can teach a subject in a specific class"""
        expanded_assignments = self.expand_teacher_subjects()
        
        if teacher not in expanded_assignments:
            return False
            
        teacher_info = expanded_assignments[teacher]
        
        # Check if teacher can teach this class
        if class_name not in teacher_info["classes"] and "All" not in teacher_info["classes"]:
            return False
            
        # Check if teacher can teach this subject
        return subject in teacher_info["subjects"]
    
    def get_available_teachers(self, subject: str, class_name: str) -> List[str]:
        """Get list of teachers who can teach a subject in a specific class"""
        available = []
        expanded_assignments = self.expand_teacher_subjects()
        
        for teacher in expanded_assignments:
            if self.can_teach(teacher, subject, class_name):
                available.append(teacher)
                
        return available
    
    def create_subject_teacher_mapping(self):
        """Create mapping of which teachers can teach which subjects in which classes"""
        mapping = {}
        
        for class_name in self.class_subjects:
            mapping[class_name] = {}
            for subject in self.class_subjects[class_name]:
                if subject in self.period_allotments and self.period_allotments[subject].get(class_name, 0) > 0:
                    available_teachers = self.get_available_teachers(subject, class_name)
                    
                    # Special rule for Conversation - must be class teacher
                    if subject == "Conversation":
                        available_teachers = [self.class_teachers.get(class_name)]
                        available_teachers = [t for t in available_teachers if t is not None]
                    
                    mapping[class_name][subject] = available_teachers
                    
        return mapping
    
    def generate_timetables(self):
        """Generate conflict-free timetables for all classes"""
        subject_teacher_mapping = self.create_subject_teacher_mapping()
        
        # Initialize timetables
        timetables = {}
        for class_name in self.class_subjects:
            timetables[class_name] = {}
            for day in self.days:
                periods = self.saturday_periods if day == "Saturday" else self.daily_periods[class_name]
                timetables[class_name][day] = [None] * periods
        
        # Track teacher assignments to avoid conflicts
        teacher_schedule = {}
        for day in self.days:
            teacher_schedule[day] = {}
            max_periods = max([self.saturday_periods if day == "Saturday" else self.daily_periods[c] for c in self.class_subjects])
            for period in range(max_periods):
                teacher_schedule[day][period] = set()
        
        # First, assign Mass PT on Saturday Period 1 for all classes
        for class_name in self.class_subjects:
            if "Mass PT" in subject_teacher_mapping[class_name]:
                timetables[class_name]["Saturday"][0] = ("Mass PT", "Anant Kalaskar")
                teacher_schedule["Saturday"][0].add("Anant Kalaskar")
        
        # Create subject requirements for each class
        class_requirements = {}
        for class_name in self.class_subjects:
            class_requirements[class_name] = []
            for subject in self.class_subjects[class_name]:
                periods_needed = self.period_allotments.get(subject, {}).get(class_name, 0)
                if periods_needed > 0 and subject != "Mass PT":  # Mass PT already assigned
                    for _ in range(periods_needed):
                        class_requirements[class_name].append(subject)
        
        # Schedule subjects using backtracking algorithm
        self.schedule_subjects(timetables, teacher_schedule, subject_teacher_mapping, class_requirements)
        
        return timetables
    
    def schedule_subjects(self, timetables, teacher_schedule, subject_teacher_mapping, class_requirements):
        """Use improved algorithm to schedule all subjects without conflicts"""
        
        # Create a priority-based scheduling approach
        # First, ensure all required subjects get their minimum periods
        
        # Track remaining requirements for each subject in each class
        remaining_requirements = {}
        for class_name in class_requirements:
            remaining_requirements[class_name] = {}
            for subject in self.class_subjects[class_name]:
                required_periods = self.period_allotments.get(subject, {}).get(class_name, 0)
                if required_periods > 0 and subject != "Mass PT":  # Mass PT already handled
                    remaining_requirements[class_name][subject] = required_periods
        
        # Schedule subjects with priority to those with fewer teacher options
        max_iterations = 100  # Prevent infinite loops
        iteration = 0
        
        while any(remaining_requirements[c] for c in remaining_requirements) and iteration < max_iterations:
            iteration += 1
            progress_made = False
            
            # Create list of all pending assignments
            pending_assignments = []
            for class_name, subjects in remaining_requirements.items():
                for subject, periods_needed in subjects.items():
                    if periods_needed > 0:
                        available_teachers = subject_teacher_mapping[class_name].get(subject, [])
                        if available_teachers:
                            # Priority: fewer teachers available = higher priority
                            priority = 1 / len(available_teachers)
                            pending_assignments.append((priority, class_name, subject, available_teachers))
            
            # Sort by priority (higher priority first)
            pending_assignments.sort(reverse=True)
            
            # Try to place one period for each subject
            for priority, class_name, subject, available_teachers in pending_assignments:
                if remaining_requirements[class_name].get(subject, 0) <= 0:
                    continue
                    
                placed = False
                
                # Try each day and period
                for day in self.days:
                    if placed:
                        break
                        
                    periods = self.saturday_periods if day == "Saturday" else self.daily_periods[class_name]
                    
                    for period in range(periods):
                        if placed:
                            break
                            
                        # Skip if slot already filled
                        if timetables[class_name][day][period] is not None:
                            continue
                        
                        # Skip Saturday period 1 (reserved for Mass PT)
                        if day == "Saturday" and period == 0:
                            continue
                        
                        # Try each available teacher
                        for teacher in available_teachers:
                            if teacher not in teacher_schedule[day][period]:
                                # Assign the subject
                                timetables[class_name][day][period] = (subject, teacher)
                                teacher_schedule[day][period].add(teacher)
                                remaining_requirements[class_name][subject] -= 1
                                if remaining_requirements[class_name][subject] <= 0:
                                    del remaining_requirements[class_name][subject]
                                placed = True
                                progress_made = True
                                break
                
                if not placed and remaining_requirements[class_name].get(subject, 0) > 0:
                    print(f"Warning: Could not place {subject} for {class_name} (still need {remaining_requirements[class_name][subject]} periods)")
            
            if not progress_made:
                break
        
        # Report any unscheduled requirements
        for class_name, subjects in remaining_requirements.items():
            for subject, periods_needed in subjects.items():
                if periods_needed > 0:
                    print(f"ERROR: {subject} for {class_name} is short by {periods_needed} periods")
        
        # Fill any remaining empty slots with available subjects/teachers
        self.fill_remaining_slots(timetables, teacher_schedule, subject_teacher_mapping)
    
    def fill_remaining_slots(self, timetables, teacher_schedule, subject_teacher_mapping):
        """Fill any remaining empty slots with appropriate subjects"""
        
        # First, try to fill with subjects that still need periods
        for class_name in timetables:
            # Count current allocations
            current_counts = {}
            for day, periods in timetables[class_name].items():
                for period_info in periods:
                    if period_info:
                        subject, teacher = period_info
                        current_counts[subject] = current_counts.get(subject, 0) + 1
            
            # Find subjects that still need more periods
            needed_subjects = []
            for subject in self.class_subjects[class_name]:
                required = self.period_allotments.get(subject, {}).get(class_name, 0)
                current = current_counts.get(subject, 0)
                if required > current:
                    for _ in range(required - current):
                        needed_subjects.append(subject)
            
            # Try to place needed subjects first
            for subject in needed_subjects:
                placed = False
                available_teachers = subject_teacher_mapping[class_name].get(subject, [])
                
                for day in self.days:
                    if placed:
                        break
                    periods = self.saturday_periods if day == "Saturday" else self.daily_periods[class_name]
                    
                    for period in range(periods):
                        if placed:
                            break
                        # Skip Saturday period 1 (Mass PT)
                        if day == "Saturday" and period == 0:
                            continue
                            
                        if timetables[class_name][day][period] is None:
                            for teacher in available_teachers:
                                if teacher not in teacher_schedule[day][period]:
                                    timetables[class_name][day][period] = (subject, teacher)
                                    teacher_schedule[day][period].add(teacher)
                                    placed = True
                                    break
        
        # Then fill any remaining empty slots with any available subjects
        for class_name in timetables:
            for day in self.days:
                periods = self.saturday_periods if day == "Saturday" else self.daily_periods[class_name]
                
                for period in range(periods):
                    # Skip Saturday period 1 (Mass PT)
                    if day == "Saturday" and period == 0:
                        continue
                        
                    if timetables[class_name][day][period] is None:
                        # Try to find any subject that can be taught by an available teacher
                        for subject, teachers in subject_teacher_mapping[class_name].items():
                            if subject == "Mass PT":  # Already handled
                                continue
                                
                            for teacher in teachers:
                                if teacher not in teacher_schedule[day][period]:
                                    timetables[class_name][day][period] = (subject, teacher)
                                    teacher_schedule[day][period].add(teacher)
                                    break
                            if timetables[class_name][day][period] is not None:
                                break
    
    def calculate_teacher_workloads(self, timetables):
        """Calculate weekly period workload for each teacher"""
        workloads = defaultdict(int)
        
        # Count regular periods
        for class_name, schedule in timetables.items():
            for day, periods in schedule.items():
                for period_info in periods:
                    if period_info:
                        subject, teacher = period_info
                        workloads[teacher] += 1
        
        # Special handling for Mass PT - Anant Kalaskar gets only 1 period total for Mass PT
        # (not 6 separate periods as it's simultaneous for all classes)
        mass_pt_count = 0
        for class_name, schedule in timetables.items():
            for day, periods in schedule.items():
                for period_info in periods:
                    if period_info and period_info[0] == "Mass PT":
                        mass_pt_count += 1
        
        if mass_pt_count > 0:
            workloads["Anant Kalaskar"] = workloads["Anant Kalaskar"] - mass_pt_count + 1
        
        return dict(workloads)
    
    def print_timetables(self, timetables):
        """Print formatted timetables"""
        print("=" * 80)
        print("SFS SCHOOL, KHAMGAON - WEEKLY TIMETABLES")
        print("=" * 80)
        
        for class_name in ["Nursery", "LKG", "UKG", "Class I", "Class II", "Class III"]:
            print(f"\n{class_name.upper()} TIMETABLE")
            print("-" * 60)
            
            # Header
            print(f"{'Period':<8}", end="")
            for day in self.days:
                print(f"{day:<12}", end="")
            print()
            print("-" * 60)
            
            # Get max periods for this class
            max_periods = max([
                self.saturday_periods if day == "Saturday" else self.daily_periods[class_name] 
                for day in self.days
            ])
            
            for period in range(max_periods):
                print(f"{period + 1:<8}", end="")
                for day in self.days:
                    periods_for_day = self.saturday_periods if day == "Saturday" else self.daily_periods[class_name]
                    if period < periods_for_day and period < len(timetables[class_name][day]):
                        slot = timetables[class_name][day][period]
                        if slot:
                            subject, teacher = slot
                            display = f"{subject[:8]}"  # Truncate long subject names
                            print(f"{display:<12}", end="")
                        else:
                            print(f"{'FREE':<12}", end="")
                    else:
                        print(f"{'-':<12}", end="")
                print()
    
    def print_teacher_workloads(self, workloads):
        """Print teacher workload summary"""
        print("\n" + "=" * 50)
        print("TEACHER WEEKLY PERIOD WORKLOAD SUMMARY")
        print("=" * 50)
        
        for teacher, periods in sorted(workloads.items()):
            print(f"{teacher:<25}: {periods:>3} periods")
        
        print(f"\nTotal periods assigned: {sum(workloads.values())}")
    
    def run(self):
        """Main execution function"""
        print("Generating conflict-free timetables for SFS School, Khamgaon...")
        print("Analyzing databases and constraints...")
        
        # Generate timetables
        timetables = self.generate_timetables()
        
        # Calculate workloads
        workloads = self.calculate_teacher_workloads(timetables)
        
        # Print results
        self.print_timetables(timetables)
        self.print_teacher_workloads(workloads)
        
        # Verify no conflicts
        self.verify_no_conflicts(timetables)
        
        return timetables, workloads
    
    def verify_no_conflicts(self, timetables):
        """Verify that no teacher is assigned to multiple classes in the same time slot"""
        print("\n" + "=" * 50)
        print("CONFLICT VERIFICATION")
        print("=" * 50)
        
        conflicts = []
        
        for day in self.days:
            # Get maximum periods for this day
            max_periods = max([
                self.saturday_periods if day == "Saturday" else self.daily_periods[c] 
                for c in self.class_subjects.keys()
            ])
            
            for period in range(max_periods):
                teacher_assignments = {}
                
                for class_name in self.class_subjects.keys():
                    periods_for_day = self.saturday_periods if day == "Saturday" else self.daily_periods[class_name]
                    
                    if period < periods_for_day and period < len(timetables[class_name][day]):
                        slot = timetables[class_name][day][period]
                        if slot:
                            subject, teacher = slot
                            
                            # Special case: Mass PT is simultaneous for all classes, not a conflict
                            if subject == "Mass PT":
                                continue
                                
                            if teacher in teacher_assignments:
                                conflicts.append({
                                    'day': day,
                                    'period': period + 1,
                                    'teacher': teacher,
                                    'classes': [teacher_assignments[teacher], class_name],
                                    'subjects': [teacher_assignments[teacher], subject]
                                })
                            else:
                                teacher_assignments[teacher] = class_name
        
        if conflicts:
            print("⚠️  CONFLICTS DETECTED:")
            for conflict in conflicts:
                print(f"  {conflict['day']} Period {conflict['period']}: {conflict['teacher']} assigned to both {conflict['classes'][0]} and {conflict['classes'][1]}")
        else:
            print("✅ NO CONFLICTS DETECTED - All timetables are conflict-free!")
            
        # Special verification for Mass PT
        print(f"\n📝 SPECIAL NOTES:")
        print(f"   • Mass PT on Saturday Period 1 is simultaneous for all classes (led by Anant Kalaskar)")
        print(f"   • This counts as only 1 period in Anant Kalaskar's total workload")

if __name__ == "__main__":
    generator = TimetableGenerator()
    generator.run()