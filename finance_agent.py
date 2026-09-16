"""
finance_agent.py
-----------------
Phase 1: Core AI Agent for Personal Finance Planner
-----------------------------------------------------
This module contains the FinanceAgent class that:
  - Loads and parses CSV expense data
  - Categorizes and totals expenses
  - Maintains a multi-turn conversation history
  - Sends financial questions to Google Gemini API
  - Returns intelligent, data-grounded financial advice

Usage (CLI):
    python finance_agent.py                    # Uses built-in sample data
    python finance_agent.py expenses.csv       # Uses a custom CSV file
"""

import csv
import os
import sys
from datetime import datetime
from collections import defaultdict
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class FinanceAgent:
    """
    An AI-powered personal finance assistant backed by Google Gemini.

    The agent:
      1. Loads expense data from a CSV file (or accepts raw rows).
      2. Computes summaries (total spend, per-category totals, date range, etc.).
      3. Maintains a rolling conversation history so follow-up questions
         have full context.
      4. Sends every user question to Gemini together with the expense
         summary, receiving actionable, number-grounded advice.
    """

    # Required CSV column names (case-insensitive during parsing)
    REQUIRED_COLUMNS = {"date", "amount", "category", "description"}

    # Google Gemini model to use
    MODEL = "gemini-3.6-flash"

    # Maximum conversation turns kept in memory (oldest are pruned first)
    MAX_HISTORY_TURNS = 20

    def __init__(self):
        # Configure Google Gemini with API key from environment
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        # Expense storage -- list of dicts with keys: date, amount, category, description
        self.expenses = []

        # Derived summary -- populated by _build_summary() after loading data
        self.summary = {}

        # Conversation history for multi-turn dialogue
        # Format: [{"role": "user"|"assistant", "content": "..."}]
        self.conversation_history = []

        # Track the currently loaded file name for display purposes
        self.loaded_file = ""

        # Detected currency symbol for display
        self.currency_symbol = "$"

    # -- Data Loading ------------------------------------------------------

    def load_csv(self, filepath):
        """
        Load and parse a CSV file of expenses.

        Expected CSV columns (case-insensitive):
            date        -- transaction date  (e.g. 2024-01-15 or 15/01/2024)
            amount      -- expense amount    (numeric, positive = expense)
            category    -- expense category  (e.g. Food, Transport, Rent)
            description -- short description (e.g. "Lunch at Subway")

        Returns:
            dict with keys success (bool), message (str),
            expense_count (int), and summary (dict).
        """
        if not os.path.exists(filepath):
            return {"success": False, "message": f"File not found: {filepath}"}

        if not filepath.lower().endswith(".csv"):
            return {"success": False, "message": "Only .csv files are supported."}

        try:
            rows = []
            with open(filepath, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)

                if reader.fieldnames is None:
                    return {"success": False, "message": "CSV file appears to be empty."}

                normalised_fields = {col.strip().lower() for col in reader.fieldnames}
                missing = self.REQUIRED_COLUMNS - normalised_fields
                if missing:
                    return {
                        "success": False,
                        "message": (
                            f"CSV is missing required columns: {', '.join(sorted(missing))}. "
                            f"Required: date, amount, category, description."
                        ),
                    }

                for line_num, raw_row in enumerate(reader, start=2):
                    row = {k.strip().lower(): v.strip() for k, v in raw_row.items() if k}

                    # Parse amount
                    try:
                        amount_str = row["amount"].replace(",", "").replace("$", "").replace("Rs.", "").replace("INR", "").strip()
                        amount = float(amount_str)
                    except ValueError:
                        print(f"  [Warning] Skipping row {line_num}: invalid amount '{row.get('amount')}'")
                        continue

                    date_str = row["date"]
                    parsed_date = self._parse_date(date_str)

                    rows.append(
                        {
                            "date": parsed_date,
                            "date_str": date_str,
                            "amount": amount,
                            "category": row["category"].strip().title(),
                            "description": row["description"].strip(),
                        }
                    )

            if not rows:
                return {"success": False, "message": "CSV file contains no valid expense rows."}

            self.expenses = rows
            self.loaded_file = os.path.basename(filepath)
            self._build_summary()
            self.conversation_history = []

            return {
                "success": True,
                "message": f"Loaded {len(rows)} expenses from '{self.loaded_file}'.",
                "expense_count": len(rows),
                "summary": self.summary,
            }

        except Exception as exc:
            return {"success": False, "message": f"Error reading CSV: {exc}"}

    def load_from_rows(self, rows, currency_symbol="$"):
        """
        Directly load pre-parsed expense rows (used by Flask backend).

        Each row dict must have: date_str, amount (float), category, description.
        Runs date parsing so monthly grouping and date range work correctly.
        """
        # Parse date strings into datetime objects for each row
        for row in rows:
            if row.get("date") is None:
                row["date"] = self._parse_date(row.get("date_str", ""))
            # Normalise category capitalisation
            row["category"] = row.get("category", "Other").strip().title()

        self.expenses = rows
        self.loaded_file = "uploaded data"
        self.currency_symbol = currency_symbol
        self._build_summary()
        self.conversation_history = []
        return {
            "success": True,
            "message": f"Loaded {len(rows)} expenses.",
            "expense_count": len(rows),
            "summary": self.summary,
        }

    # -- Summary Building --------------------------------------------------

    def _build_summary(self):
        """
        Compute expense statistics from self.expenses and store in self.summary.
        """
        if not self.expenses:
            self.summary = {}
            return

        total = 0.0
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        monthly_totals = defaultdict(float)
        dates = []

        for exp in self.expenses:
            amt = exp["amount"]
            cat = exp["category"]
            total += amt
            category_totals[cat] += amt
            category_counts[cat] += 1

            if isinstance(exp["date"], datetime):
                month_key = exp["date"].strftime("%Y-%m")
                dates.append(exp["date"])
            else:
                month_key = exp["date_str"][:7] if len(exp["date_str"]) >= 7 else "Unknown"

            monthly_totals[month_key] += amt

        sorted_expenses = sorted(self.expenses, key=lambda x: x["amount"], reverse=True)

        if dates:
            min_date = min(dates).strftime("%Y-%m-%d")
            max_date = max(dates).strftime("%Y-%m-%d")
            date_range_str = f"{min_date} to {max_date}"
        else:
            date_range_str = "Unknown date range"

        top_category = max(category_totals, key=category_totals.get) if category_totals else "N/A"

        self.summary = {
            "total_amount": round(total, 2),
            "expense_count": len(self.expenses),
            "category_totals": {k: round(v, 2) for k, v in sorted(category_totals.items(), key=lambda x: -x[1])},
            "category_counts": dict(category_counts),
            "top_category": top_category,
            "top_expenses": [
                {
                    "description": e["description"],
                    "amount": e["amount"],
                    "category": e["category"],
                    "date": e["date_str"],
                }
                for e in sorted_expenses[:5]
            ],
            "date_range": date_range_str,
            "monthly_totals": {k: round(v, 2) for k, v in sorted(monthly_totals.items())},
            "average_expense": round(total / len(self.expenses), 2),
            "largest_expense": {
                "description": sorted_expenses[0]["description"],
                "amount": sorted_expenses[0]["amount"],
                "category": sorted_expenses[0]["category"],
                "date": sorted_expenses[0]["date_str"],
            },
            "smallest_expense": {
                "description": sorted_expenses[-1]["description"],
                "amount": sorted_expenses[-1]["amount"],
                "category": sorted_expenses[-1]["category"],
                "date": sorted_expenses[-1]["date_str"],
            },
        }

    def _format_summary_for_claude(self):
        """
        Format self.summary into a human-readable text block that Claude
        can use to ground its answers with actual numbers.
        """
        if not self.summary:
            return "No expense data loaded yet."

        s = self.summary
        lines = [
            "=== EXPENSE DATA SUMMARY ===",
            f"File: {self.loaded_file}",
            f"Date Range: {s['date_range']}",
            f"Total Expenses: ${s['total_amount']:,.2f}",
            f"Number of Transactions: {s['expense_count']}",
            f"Average per Transaction: ${s['average_expense']:,.2f}",
            "",
            "--- Spending by Category ---",
        ]

        for cat, total in s["category_totals"].items():
            count = s["category_counts"].get(cat, 0)
            pct = (total / s["total_amount"] * 100) if s["total_amount"] > 0 else 0
            lines.append(f"  {cat}: ${total:,.2f}  ({count} transactions, {pct:.1f}% of total)")

        lines += [
            "",
            f"Top Spending Category: {s['top_category']}",
            "",
            "--- Monthly Totals ---",
        ]
        for month, total in s["monthly_totals"].items():
            lines.append(f"  {month}: ${total:,.2f}")

        lines += [
            "",
            "--- Top 5 Individual Expenses ---",
        ]
        for i, exp in enumerate(s["top_expenses"], 1):
            lines.append(
                f"  {i}. {exp['description']} ({exp['category']}) -- ${exp['amount']:,.2f} on {exp['date']}"
            )

        lines += [
            "",
            f"Largest Single Expense: {s['largest_expense']['description']} -- ${s['largest_expense']['amount']:,.2f}",
            f"Smallest Single Expense: {s['smallest_expense']['description']} -- ${s['smallest_expense']['amount']:,.2f}",
            "=== END OF SUMMARY ===",
        ]

        return "\n".join(lines)

    # -- Claude Integration ------------------------------------------------

    def _get_system_prompt(self):
        """
        Build the system prompt that tells Gemini its role and embeds
        the live expense summary as context.
        """
        expense_context = self._format_summary_for_claude()

        return f"""You are a personal finance analyst. The user has uploaded their expense data shown below. Your job is to answer their questions accurately and concisely using that data.

--- EXPENSE DATA ---
{expense_context}
--- END OF DATA ---

## HOW TO RESPOND

Answer ONLY what the user asked. Match the format to the question:

- **Single fact** (e.g. "what is my total?") → one sentence with the number. Nothing else.
- **Ranked list** (e.g. "top 5 expenses") → a short numbered or bullet list. No extra sections.
- **Comparison** (e.g. "which month was highest?") → state the answer, then a small table if useful.
- **Breakdown** (e.g. "show spending by category") → a markdown table with the relevant columns.
- **Advice / how to save** → 2-3 concrete, numbered steps with specific dollar amounts from the data.
- **Yes/No question** → answer directly, then one sentence of supporting data.

## RULES

1. **Answer the specific question first.** Don't start with a summary of everything.
2. **Use the actual numbers** from the data — never invent or estimate figures.
3. **Bold all dollar amounts, percentages, and key metrics** inline.
4. **Keep it short.** If the answer is one number, say one number. If it needs a table, use a table. Do not pad responses with sections the user didn't ask for.
5. Do NOT add unrequested sections like "Key Insights", "Recommendations", or "Quick Takeaway" unless the user specifically asks for advice or recommendations.
6. If the user asks a follow-up (e.g. "what about last month?"), use the conversation context to understand what they mean.
7. If no data is loaded, respond only with: "Please upload a CSV expense file first."
8. Sort any ranked data highest to lowest.
9. Format currency with the appropriate symbol from the data.
"""

    def ask_agent(self, question):
        """
        Send a user question to Google Gemini and return the agent's response.

        The full conversation history is included so Gemini maintains
        context across multiple questions in the same session.

        Args:
            question: The user's natural-language financial question.

        Returns:
            The agent's response string.
        """
        if not self.expenses:
            return (
                "No expense data is loaded yet. Please provide a CSV file first "
                "so I can analyse your finances."
            )

        self.conversation_history.append({"role": "user", "content": question})

        if len(self.conversation_history) > self.MAX_HISTORY_TURNS * 2:
            self.conversation_history = self.conversation_history[-(self.MAX_HISTORY_TURNS * 2):]

        try:
            # Build Gemini-compatible history: map roles and prepend system prompt
            # New google-genai SDK uses 'user'/'model' roles (not 'assistant')
            gemini_history = []
            for msg in self.conversation_history[:-1]:  # exclude latest user message
                role = "model" if msg["role"] == "assistant" else "user"
                gemini_history.append(
                    types.Content(role=role, parts=[types.Part(text=msg["content"])])
                )

            # Start a chat session with existing history
            chat = self.client.chats.create(
                model=self.MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=self._get_system_prompt(),
                    max_output_tokens=3000,
                    temperature=0.4,
                ),
                history=gemini_history,
            )

            # Send the latest user question
            response = chat.send_message(question)

            answer = response.text
            self.conversation_history.append({"role": "assistant", "content": answer})
            return answer

        except Exception as exc:
            self.conversation_history.pop()
            raise RuntimeError(f"Gemini API error: {exc}") from exc

    def reset_conversation(self):
        """Clear conversation history (keeps expense data intact)."""
        self.conversation_history = []
        print("Conversation history cleared.")

    def get_summary(self):
        """Return the computed expense summary dict."""
        return self.summary

    # -- Helpers ----------------------------------------------------------

    @staticmethod
    def _parse_date(date_str):
        """
        Attempt to parse a date string in several common formats.
        Returns a datetime on success, or the original string on failure.
        """
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%d %b %Y",
            "%B %d, %Y",
            "%Y/%m/%d",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return date_str


# -- CLI entry-point -----------------------------------------------------------

def main():
    """
    Interactive command-line interface for the Finance Agent.

    Usage:
        python finance_agent.py                # auto-loads sample_expenses.csv if present
        python finance_agent.py mydata.csv     # load a specific CSV file
    """
    print("=" * 60)
    print("  Personal Finance Planner -- AI Agent (Phase 1)")
    print("=" * 60)
    print()

    agent = FinanceAgent()

    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    elif os.path.exists("sample_expenses.csv"):
        csv_path = "sample_expenses.csv"
        print(f"Auto-detected sample data: {csv_path}")
    else:
        csv_path = input("Enter path to your expense CSV file: ").strip().strip('"')

    result = agent.load_csv(csv_path)
    if not result["success"]:
        print(f"\nError: {result['message']}")
        sys.exit(1)

    print(f"\n{result['message']}")
    print()

    s = agent.get_summary()
    print("-" * 60)
    print(f"  Date Range  : {s['date_range']}")
    print(f"  Transactions: {s['expense_count']}")
    print(f"  Total Spent : ${s['total_amount']:,.2f}")
    print(f"  Top Category: {s['top_category']} (${s['category_totals'].get(s['top_category'], 0):,.2f})")
    print("-" * 60)
    print()
    print("Ask me anything about your expenses! Type 'quit' to exit,")
    print("'summary' to see the full breakdown, or 'reset' to clear chat history.")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        lower = user_input.lower()

        if lower in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        elif lower == "summary":
            print("\n" + agent._format_summary_for_claude() + "\n")
            continue

        elif lower == "reset":
            agent.reset_conversation()
            continue

        print("\nAgent: ", end="", flush=True)
        try:
            answer = agent.ask_agent(user_input)
            print(answer)
        except RuntimeError as e:
            print(f"Error: {e}")
        print()


if __name__ == "__main__":
    main()
