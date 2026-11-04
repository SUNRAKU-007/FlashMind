from agent import build_reader_agent , build_search_agent , writer_chain , critic_chain
from rich.panel import Panel
from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule
import time

console=Console()

def timed_step(name, function, *args, **kwargs):
    start_time = time.perf_counter()
    console.print(f"\n[yellow]Starting: {name}...[/yellow]")
    try:
        result = function(*args, **kwargs)
        elapsed = time.perf_counter() - start_time
        console.print(
            f"[green]Completed: {name} "
            f"in {elapsed:.2f} seconds.[/green]" )
        return result
    except Exception as error:
        elapsed = time.perf_counter() - start_time
        console.print(
            f"[bold red]Failed: {name} "
            f"after {elapsed:.2f} seconds.[/bold red]")
        raise

def run_research_pipeline(topic:str)->dict:
    state={} # where i will fill all the details
    
    #search agent working
    total_start=time.perf_counter()
    
    console.print()
    console.rule("[bold cyan] Step 1: SEARCH AGENT IS WORKING [/bold cyan]")
    
    
    search_agent= timed_step(
        "Building search agent",
        build_search_agent,
    )
    search_result=timed_step(
        "Executing web search",
        search_agent.invoke,
        {
        "messages":[(
            "user",
            f"Find recent , reliable and detailed information about: {topic}"
            )]
    },
    )
    
    state["search_result"]= search_result['messages'][-1].content
    
    console.print(
        Panel(
            str(state["search_result"]),
            title="Search Results",
            border_style="cyan",
        )
    )

    # step 2 - reader agent
    console.print()
    console.rule("[bold cyan]STEP 2: READER AGENT[/bold cyan]")
    
    reader_agent=timed_step(
        "Building reader agent",
        build_reader_agent,
        )
    reader_result=timed_step(
        "Scraping relevant resources",
        reader_agent.invoke,
        {
        "messages": [("user",
                      f"Based on the following search results about '{topic}', "
                      f"pick the most relevant URL and scrape it for deeper content. \n\n"
                      f"Search Results:\n{state['search_result'][:800]}"
                    )]
    },
        )
    
    state['scraped_content']=reader_result['messages'][-1].content
    
    console.print(
        Panel(
            str(state["scraped_content"])[:4000],
            title="Scrapped Content Preview",
            border_style="cyan",
        )
    )
    
    
    # step 3 - writer chain
    
    console.print()
    console.rule("[bold cyan]Step 3: REPORT WRITER[/bold cyan]")
    
    research_combined=(
        f"SEARCH RESULTS : \n {state['search_result']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']} \n\n"
    )
    
    state["report"]=timed_step(
        "Generating research report",
        writer_chain.invoke,
        {
        "topic": topic,
        "research": research_combined,
    },
        )
    
    console.print(
        Panel(
            str(state["report"]),
            title="Final Research Report",
            border_style="green",
        )
    )
    
    
    #critic report
    console.print()
    console.rule("[bold cyan]Step 4: CRITIC REVIEW[/bold cyan]")
    
    
    state["feedback"]=timed_step(
        "Reviewing research report",
        critic_chain.invoke,
        {
        "report":state['report']
    },
        )
    
    console.print(
        Panel(
            str(state["feedback"]),
            title="Critic Feedback",
            border_style="magenta",
        )
    )
    total_elapsed=time.perf_counter()-total_start
    
    console.print()
    console.rule("[bold green]Research Completed[/bold green]")
    
    console.print(
        Panel(
            f"[bold green]Research completed successfully![/bold green]\n\n"
            f"Topic: {topic}\n"
            f"Total execution time: {total_elapsed:.2f} seconds",
            title="Pipeline Summary", 
            border_style="green",
        )
    )
    
    return state
if __name__ == "__main__":
    try:
        topic = console.input(
            "\n[bold cyan]Enter a research topic:[/bold cyan] "
        ).strip()

        if not topic:
            console.print(
                Panel(
                    "Please enter a research topic.",
                    title="Input Required",
                    border_style="yellow",
                )
            )
        else:
            results = run_research_pipeline(topic)

    except KeyboardInterrupt:
        console.print("\n[yellow]Research cancelled by user.[/yellow]")

    except Exception as error:
        console.print()
        console.print(
            Panel(
                f"[bold red]The research pipeline could not continue.[/bold red]"
                f"\n\n[white]{error}[/white]"
                "\n\n[dim]Check the error details and retry when the "
                "underlying issue has been resolved.[/dim]",
                title="[bold red]Pipeline Error[/bold red]",
                border_style="red",
                padding=(1, 2),
            )
        )
    

    
    