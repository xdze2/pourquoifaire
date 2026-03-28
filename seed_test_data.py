#!/usr/bin/env python3
"""Seed the database with realistic test data for projects and tasks."""

from how_and_why.api import add_node, import_nodes
from pathlib import Path

# Rich test data representing real project structures
TEST_DATA = [
    # Home Automation Project
    {
        "description": "Set up home automation system",
        "context": "Replace old switches with smart ones. Goal: control lights and temperature via phone app.",
        "status": "pending",
        "type": "project",
    },
    {
        "description": "Research smart light options",
        "context": "Need zigbee compatible. Budget under $50 per bulb. Check Philips Hue, LIFX, and Wyze reviews.",
        "status": "in_progress",
        "type": "task",
    },
    {
        "description": "Install home hub",
        "context": "Need a central hub to control all devices. Considering Home Assistant or Apple HomeKit.",
        "status": "pending",
        "type": "task",
    },
    # Fitness Goal Project
    {
        "description": "Get fit - 100 push-ups challenge",
        "context": "12-week program. Start with 50 push-ups baseline. Goal: 100 consecutive.",
        "status": "pending",
        "type": "project",
    },
    {
        "description": "Baseline fitness test",
        "context": "Measure current push-ups, pull-ups, plank time, and 5K run time.",
        "status": "in_progress",
        "type": "task",
    },
    {
        "description": "Buy exercise equipment",
        "context": "Pull-up bar, resistance bands, dumbbells",
        "status": "pending",
        "type": "task",
    },
    {
        "description": "Schedule gym membership",
        "context": "Find nearby 24/7 gym with good reviews",
        "status": "pending",
        "type": "task",
    },
    # Home Renovation Project
    {
        "description": "Kitchen renovation",
        "context": "Update counters, cabinets, and appliances. Timeline: 2 months. Budget: $15k",
        "status": "stuck",
        "type": "project",
    },
    {
        "description": "Get kitchen contractor quotes",
        "context": "Need at least 3 quotes. Compare prices and timeline. Currently stuck - contractors overbooked.",
        "status": "stuck",
        "type": "task",
    },
    {
        "description": "Choose cabinet color and style",
        "context": "Wife wants white, I prefer dark. Pinterest board created.",
        "status": "pending",
        "type": "task",
    },
    {
        "description": "Order new kitchen appliances",
        "context": "Stove, refrigerator, dishwasher. Check for sales before ordering.",
        "status": "pending",
        "type": "task",
    },
    # Learning Project
    {
        "description": "Learn Python for data science",
        "context": "Goal: Build predictive models. Timeline: 3 months",
        "status": "in_progress",
        "type": "project",
    },
    {
        "description": "Complete Python basics course",
        "context": "DataCamp course - currently at week 3/5",
        "status": "in_progress",
        "type": "task",
    },
    {
        "description": "Learn pandas and data wrangling",
        "context": "Focus on groupby, merge, and pivot operations",
        "status": "pending",
        "type": "task",
    },
    {
        "description": "First machine learning project",
        "context": "Kaggle housing price prediction competition",
        "status": "pending",
        "type": "task",
    },
    # Work Project
    {
        "description": "Launch new API endpoint",
        "context": "Complete authentication system with JWT. Goal: production ready",
        "status": "in_progress",
        "type": "project",
    },
    {
        "description": "Implement JWT authentication",
        "context": "Use jsonwebtoken library. Support refresh tokens.",
        "status": "in_progress",
        "type": "task",
    },
    {
        "description": "Write unit tests for auth module",
        "context": "Target: 95% code coverage",
        "status": "pending",
        "type": "task",
    },
    {
        "description": "Code review and documentation",
        "context": "Update README with API examples. Get team approval.",
        "status": "pending",
        "type": "task",
    },
    # Personal Development
    {
        "description": "Read 12 books this year",
        "context": "Mix of fiction and non-fiction. 1 book per month target.",
        "status": "in_progress",
        "type": "project",
    },
    {
        "description": "Finish current book: Atomic Habits",
        "context": "Currently at chapter 8. Taking notes on habits loop.",
        "status": "in_progress",
        "type": "task",
    },
    {
        "description": "Start next book: The Midnight Library",
        "context": "Fiction - want something lighter for change of pace",
        "status": "pending",
        "type": "task",
    },
]


def seed_database():
    """Add test data to the database."""
    print("Seeding database with test data...\n")

    for i, data in enumerate(TEST_DATA, 1):
        node_id = add_node(
            description=data["description"],
            context=data.get("context", ""),
            status=data.get("status", "pending"),
            type=data.get("type", "task"),
        )
        print(f"✓ Added: {data['description'][:50]}... (ID: {node_id})")

    print(f"\n✅ Successfully seeded {len(TEST_DATA)} test nodes!")
    print("\nYou can now test with:")
    print("  how_and_why search --query 'kitchen'")
    print("  how_and_why find --query 'home automation'")
    print("  how_and_why find --query 'stuck projects'")


if __name__ == "__main__":
    seed_database()
