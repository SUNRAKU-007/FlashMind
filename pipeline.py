from agent import build_reader_agent , build_search_agent , writer_chain , critic_chain
from rich.panel import Panel
from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule

console=Console()

def run_research_pipeline(topic:str)->str:
    state={} # where i will fill all the details
    
    #search agent working
    
    print("\n"+"="*50+"\n")
    print("step 1- search agent is working ...")
    
    print("="*50)
    
    search_agent= build_search_agent()
    search_result=search_agent.invoke({
        "messages":[("user", f"Find recent , reliable and detailed information about: {topic}")]
    })
    
    state["search_result"]= search_result['messages'][-1].content
    
    print("\n Search result", state['search_result'])

    # step 2 - reader agent
    print("\n"+"="*50+"\n")
    print("step 2- reader agent is scraping top resouces ...")
        
    print("="*50)
    
    reader_agent=build_reader_agent()
    reader_result=reader_agent.invoke({
        "messages": [("user",
                      f"Based on the following search results about '{topic}', "
                      f"pick the most relevant URL and scrape it for deeper content. \n\n"
                      f"Search Results:\n{state['search_result'][:800]}"
                    )]
    })
    
    state['scraped_content']=reader_result['messages'][-1].content
    
    print("scraped content\n",state['scraped_content'])
    
    
    # step 3 - writer chain
    
    print("\n"+"="*50+"\n")
    print("step 3- writer is drafting the report ...")
        
    print("="*50)
    
    research_combined=(
        f"SEARCH RESULTS : \n {state['search_result']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']} \n\n"
    )
    
    state["report"]=writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })
    
    print("\n FINAL REPORT :\n", state['report'])
    
    
    #critic report
    print("\n"+"="*50+"\n")
    print("step 4- critic is reviweing the report ...")
        
    print("="*50)
    
    state["feedback"]=critic_chain.invoke({
        "report":state['report']
    })
    
    print("\n Critic Report \n",state['feedback'])
    
    
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
    

    
    