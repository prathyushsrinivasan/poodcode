# Master Prompt: Build My Personal Offline Coding Interview Desktop Application

## Project Overview

I want you to build a **desktop application** that serves as my personal coding interview and algorithm practice platform. This is **not** intended to compete with LeetCode or be released publicly. It is for **my own learning, long-term growth, and interview preparation**.

Build the entire application in a single session. Do not stop after planning, asking for confirmation, or completing only one phase. Make all necessary architectural decisions yourself, implement every feature end-to-end, resolve issues autonomously, and continue until the application is fully functional. Only pause if you encounter a blocker that genuinely requires information only I can provide.

The application's primary goal is to maximize learning efficiency, identify weaknesses, encourage spaced repetition, and help me become a better software engineer.


# Core Principles

Prioritize:

* Simplicity
* Offline-first
* Fast startup
* Excellent UX
* Maintainable architecture
* Modular code
* Clean design
* Extensible architecture

Avoid unnecessary complexity.

No social features.

No leaderboards.

No chat.

No cloud dependency.

No gamification beyond what genuinely improves motivation.

---

# Technology Stack

Preferred stack:

Desktop

* Tauri

Frontend

* React + TypeScript

Backend

* Rust (preferred for Tauri)

Database

* SQLite

Editor

* Monaco Editor

Charts

* Apache ECharts

Storage

* Local filesystem

Markdown rendering

* Markdown support for notes and editorials

Use clean architecture and separate:

* UI
* Business logic
* Database
* Code execution

Everything should be modular.

---

# Application Sections

## 1. Dashboard

When opening the application, display:

Today's goals

Example

* Solve 2 Easy
* Solve 1 Medium
* Review 3 problems
* Read 1 editorial

Show:

* Problems solved today
* Total study time
* Current streak
* Revision due today
* Weakest topic
* Suggested next problem

---

## 2. Problem Library

A searchable database.

Each problem stores:

* Title
* Difficulty
* Topics
* Subtopics
* Company tags
* Description
* Constraints
* Examples
* Notes
* Editorial
* Hidden test cases
* User-created test cases
* Favorite
* Solved status
* Confidence level
* Last solved
* Review schedule
* Time taken
* Number of attempts
* Number of successful submissions

Support filters:

Difficulty

Topics

Companies

Status

Favorites

Needs Review

Weak Confidence

Recently Added

Recently Solved

---

## 3. Code Editor

Embed Monaco Editor.

Support:

* Multiple tabs
* Themes
* Font size
* Line numbers
* Syntax highlighting
* Auto-complete
* Code formatting
* Keyboard shortcuts
* Find and replace
* Minimap
* Split editor

Languages:

* Java
* Python
* C++
* JavaScript
* TypeScript
* Go
* Rust
* Kotlin
* C#

---

## 4. Code Execution

Support:

Run

Uses custom test cases.

Submit

Runs hidden test cases.

Display:

* Passed
* Failed
* Runtime
* Memory
* Failed test case
* Expected output
* Actual output

Architecture should make it easy to add languages later.

---

## 5. Test Case Manager

Allow:

* Create test cases
* Edit
* Delete
* Save
* Import
* Export
* Random test generation
* Edge-case generation

---

## 6. Notes System

Each problem has markdown notes.

Support:

* Markdown
* Code blocks
* Images
* Checklists
* Tables
* Links

Suggested note sections:

Key Idea

Mistakes

Complexity

Alternative Solutions

Patterns

Things To Remember

---

## 7. Revision System

Implement spaced repetition.

Each solved problem automatically enters review.

Example schedule:

Tomorrow

3 days

7 days

14 days

30 days

90 days

Allow manual adjustments.

Show review queue every day.

---

## 8. Attempt History

Every submission is saved.

Record:

Timestamp

Code

Runtime

Memory

Wrong answers

Compilation errors

Notes

Display progression over time.

---

## 9. Hint System

Never reveal the full solution immediately.

Provide hints incrementally.

Example:

Hint 1

High-level idea.

Hint 2

Relevant data structure.

Hint 3

Algorithm direction.

Hint 4

Pseudo-code.

Only reveal the full solution when explicitly requested.

---


## 11. Complexity Analyzer

Estimate:

Time Complexity

Space Complexity

Compare against optimal complexity.

Example:

Your solution:
O(n²)

Optimal:
O(n log n)

Explain why.

---

## 12. Statistics Dashboard

Display:

Problems solved

Per difficulty

Per topic

Average solve time

Acceptance rate

Review completion

Heatmap

Weekly activity

Monthly activity

Language usage

Most difficult topics

Weakest topics

Strongest topics

---

## 13. Learning Timeline

Track progress.

Example:

Month

Problems solved

Concepts learned

Average solve time

Topics mastered

---

## 14. Interview Mode

Simulate interviews.

Features:

45-minute timer

No hints

No autocomplete (optional)

No editor suggestions

Lock after timer expires

Summary afterward.

---

## 15. Random Practice

Generate random problems using filters.

Examples:

Random Medium Graph

Random Hard DP

Problems not solved in 60 days

Failed twice

Weak confidence

---

## 16. Solution Library

Allow multiple stored approaches.

Example:

Brute Force

Optimized

Recursive

Iterative

Dynamic Programming

Two Pointers

Store complexity for each.

---

## 17. Code Comparison

Compare:

First attempt

Latest attempt

Best solution

Highlight:

Improvements

Removed complexity

Cleaner code

Performance gains

---

## 18. Search by Weakness

Support queries like:

Problems over 45 minutes

Problems failed twice

Graphs not reviewed

Medium Trees

Dynamic Programming

Low confidence

Never solved optimally

---

## 19. Company Preparation

Allow grouped problem lists.

Examples:

Amazon

Google

Meta

Microsoft

Adobe

Bloomberg

Allow custom company lists.

---

## 20. Contest Mode

Support custom contests.

Features:

Timer

Problem set

Score

Summary

History

---

## 21. Offline Mode

Everything must work offline.

Problems

Notes

Statistics

Execution

Search

Database

No internet required.

---

## 22. Visual Debugger (Advanced)

Visualize execution for:

Arrays

Matrices

Linked Lists

Trees

Binary Trees

Graphs

Queues

Stacks

Heaps

Pointers

Show state changes step-by-step.

---

## 23. Learning Recommendations

Based on performance.

Examples:

You struggle with Graphs.

Recommended:

* BFS
* DFS
* Topological Sort

Before Hard DP:

Practice:

* Fibonacci
* Climbing Stairs
* House Robber

---

# Database Design

Design a normalized SQLite schema.

Include tables for:

Problems

Attempts

Solutions

Notes

Reviews

Tags

Companies

Statistics

Settings

Daily sessions

Revision schedule

Test cases

History

Future-proof the schema.

---

# User Experience

Prioritize:

Minimal clicks

Keyboard shortcuts

Fast navigation

Command palette

Responsive UI

Autosave

Session restore

Persistent editor state

Smooth animations

Dark mode

---



# Development Process

Do **not** generate the entire application in one step.

Instead:

1. Plan the architecture.
2. Design the database.
3. Define modules and folder structure.
4. Generate an implementation roadmap.
5. Build incrementally.
6. Keep each feature modular and well documented.
7. Write clean, production-quality code with comments only where they add value.
8. Include tests for critical business logic.

Before implementing any major feature, explain the design decisions and trade-offs.
More than anything else, the quality of the problems are the foremost important part. 
