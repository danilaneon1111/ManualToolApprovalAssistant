from rich.console import Console
from app.config import settings
from app.manual_chain import ManualToolApprovalChain

console = Console()

def run_cli():
    chain = ManualToolApprovalChain()
    console.print("[bold]Manual Tool Approval Assistant (CLI) запущен.[/bold]")
    console.print("Команды: exit / quit\n")

    while True:
        try:
            user_text = console.input("\n[cyan]Ты> [/cyan]").strip()
            if user_text.lower() in {"exit", "quit"}:
                break
            answer = chain.invoke(user_text)
            console.print(f"[green]Бот>[/green] {answer}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Ошибка:[/red] {e}")

if __name__ == "__main__":
    if settings.interface == "cli":
        run_cli()
    else:
        raise RuntimeError("Выбран не CLI интерфейс. Для других интерфейсов добавь отдельный модуль.")
