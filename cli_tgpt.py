#!/usr/bin/env python3
"""
KIND v4 CLI with TGPT Engine
"""

from kind_tgpt_engine import kind
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
import sys

console = Console()

def print_banner():
    banner = Panel.fit(
        "[bold cyan]🧠 KIND v4 GODMODE with TGPT Engine[/bold cyan]\n"
        "[green]Self-Learning AI | Memory System | Terminal Optimized[/green]\n"
        f"[yellow]Total Solutions: {kind.memory.memory['stats']['total_interactions']}[/yellow]\n"
        f"[blue]TGPT: {'✅ Available' if kind.tgpt.available else '⚠️ Fallback Mode'}[/blue]",
        border_style="cyan"
    )
    console.print(banner)
    console.print("[dim]Type 'exit' to quit, 'stats' for system info, 'clear' to clear screen[/dim]\n")

def show_stats():
    stats = kind.get_stats()
    table = Table(title="KIND System Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in stats.items():
        table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(table)

def main():
    print_banner()
    
    while True:
        try:
            problem = Prompt.ask("\n[bold cyan]💬 You[/bold cyan]")
            
            if problem.lower() in ['exit', 'quit']:
                console.print("\n[bold green]👋 Goodbye! Memory preserved for next session.[/bold green]")
                break
            elif problem.lower() == 'stats':
                show_stats()
                continue
            elif problem.lower() == 'clear':
                console.clear()
                print_banner()
                continue
            
            console.print("\n[bold yellow]🧠 KIND is thinking...[/bold yellow]")
            solution = kind.solve(problem, source="cli")
            
            console.print(Panel(
                Markdown(solution),
                title="[bold green]🤖 KIND AI[/bold green]",
                border_style="green"
            ))
            
        except KeyboardInterrupt:
            console.print("\n\n[bold red]Interrupted. Exiting...[/bold red]")
            break
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")

if __name__ == "__main__":
    main()
