#!/usr/bin/env python3
"""
Analyze LLM simulation statistics from existing log files.
This script reads simulation log files and calculates statistics for action types.
"""

import json
import glob

def calculate_action_statistics(interaction_log):
    """
    Calculate statistics for CHOOSE_RECOMMENDATION, REFINE_RECOMMENDATION, and FORMULATE_NEW actions.
    
    Args:
        interaction_log (list): The complete interaction log from the simulation
    
    Returns:
        dict: Statistics about action types
    """
    action_counts = {
        "CHOOSE_RECOMMENDATION": 0,
        "REFINE_RECOMMENDATION": 0,
        "FORMULATE_NEW": 0
    }
    
    total_actions = 0
    
    for turn_data in interaction_log:
        decision = turn_data.get("decision", {})
        
        # Check for cold start decision
        if "first_action_type" in decision:
            action_type = decision["first_action_type"]
            if action_type in action_counts:
                action_counts[action_type] += 1
                total_actions += 1
        
        # Check for interaction turn decisions
        if "next_action_type" in decision:
            action_type = decision["next_action_type"]
            if action_type in action_counts:
                action_counts[action_type] += 1
                total_actions += 1
    
    # Calculate percentages
    statistics = {
        "total_actions": total_actions,
        "action_counts": action_counts,
        "action_percentages": {}
    }
    
    if total_actions > 0:
        for action_type, count in action_counts.items():
            percentage = (count / total_actions) * 100
            statistics["action_percentages"][action_type] = round(percentage, 2)
    
    return statistics

def analyze_all_simulation_logs():
    """Analyze all simulation log files in the current directory."""
    
    # Find all simulation log files, excluding evaluation files
    log_files = [f for f in glob.glob("simulation_log_*.json") if not f.endswith("_EVALUATION.json")]
    
    if not log_files:
        print("No simulation log files found in current directory.")
        return
    
    print("📊 LLM Simulation Action Statistics Analysis")
    print("=" * 60)
    
    overall_stats = {
        "CHOOSE_RECOMMENDATION": 0,
        "REFINE_RECOMMENDATION": 0, 
        "FORMULATE_NEW": 0
    }
    overall_total = 0
    
    for log_file in sorted(log_files):
        print(f"\n📁 File: {log_file}")
        print("-" * 40)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if statistics already exist in the file
            if "action_statistics" in data:
                stats = data["action_statistics"]
                print("📊 Statistics from saved data:")
            else:
                # Calculate statistics from interaction log
                interaction_log = data.get("interaction_log", [])
                stats = calculate_action_statistics(interaction_log)
                print("📊 Calculated statistics:")
            
            # Display individual file statistics
            print(f"Total Actions: {stats['total_actions']}")
            print("Action Distribution:")
            for action_type, count in stats['action_counts'].items():
                percentage = stats['action_percentages'].get(action_type, 0)
                print(f"  {action_type}: {count} ({percentage}%)")
                # Add to overall statistics
                overall_stats[action_type] += count
            
            overall_total += stats['total_actions']
            
            # Display metadata if available
            metadata = data.get("metadata", {})
            if metadata:
                print(f"\nMetadata:")
                print(f"  Database: {metadata.get('db_id', 'N/A')}")
                print(f"  Mode: {metadata.get('simulation_mode', 'N/A')}")
                print(f"  Timestamp: {metadata.get('timestamp', 'N/A')}")
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading {log_file}: {e}")
    

if __name__ == "__main__":
    analyze_all_simulation_logs()