from fasthtml.common import *

app,rt,todos,Todo = fast_app(
    'data/todos.db',
    hdrs=[
        Socials(site_name="Ai-Evals", title="AI-Evals", image="https://res.cloudinary.com/dwxrm0iul/image/upload/v1731538464/tweet-1733553161884127435_2_cpectu.png", card="summary_large_image", description="Struggling with LLM Evals? Learn how to do them correctly."),
        Style(':root { --pico-font-size: 100%; }'),
        Style('div[data-style="clean"] { padding-top: 0 !important; padding-bottom: 8px !important; }')
    ],
    id=int, title=str, done=bool, upvotes=int, pk='id')

id_curr = 'current-todo'
def tid(id): return f'todo-{id}'

@patch
def __ft__(self:Todo):
    topic_display = self.title
    upvote_link = AX('👍', f'/upvote/{self.id}', id=tid(self.id), cls='upvote-link')
    upvotes_display = f'{self.upvotes or 0}'
    return Tr(Td(topic_display), Td(upvotes_display), Td(upvote_link), id=tid(self.id))

def mk_input(**kw): return Input(id="new-title", name="title", placeholder="New Item", required=True, **kw)

# Read the contents of form.html
def read_form_html():
    with open('form.html', 'r') as file:
        return file.read()
    
@rt("/healthcheck")
def healthcheck():
    return "ok"

@rt("/")
def get(page: int = 1):
    items_per_page = 10
    start = (page - 1) * items_per_page
    end = start + items_per_page

    # Introductory information
    intro = Div(
        P("Hi, I’m ", A("Hamel Husain", href="https://hamel.dev/"), ". I ", 
          A("", href="https://parlance-labs.com/"), 
          "help companies build AI products. Most companies struggle with AI because they're missing one crucial piece: proper evaluations. ",
          "However, there is very little training on how to do them correctly. I’ve written about this ",
          A("here", href="https://hamel.dev/blog/posts/llm-judge/"), " and ",
          A("here", href="https://hamel.dev/blog/posts/evals/"), ", but people want to learn more."
        ),
        Div(
            Img(src="https://res.cloudinary.com/dwxrm0iul/image/upload/v1731538464/tweet-1733553161884127435_2_cpectu.png", style="width:33%; display: block; margin: 0 auto;"), 
            cls='tweet'
        ),
        Br(),
        P("Before I go off into a cave and write even more about evals, I want to know what questions you have."),
        H2("Step 1:Tell me what you want to learn"),
        P("Upvote or add a topic below.  Paginate to see more. I'll write about the top voted topics first."),
    )

    add = Form(Group(mk_input(), Button("Add")),
               hx_post="/", target_id='todo-list', hx_swap="beforeend")
    table_header = Tr(Th("Topic"), Th("Num Upvotes"), Th("Upvote"))
    
    # Sort todos by upvotes in descending order
    sorted_todos = sorted(todos(), key=lambda todo: todo.upvotes or 0, reverse=True)
    
    # Paginate topics
    table_body = [todo.__ft__() for todo in sorted_todos[start:end]]

    # Pagination controls
    total_pages = (len(sorted_todos) + items_per_page - 1) // items_per_page
    pagination_controls = Div(
        Span(f"Page {page} of {total_pages} | "),
        A("Previous", href=f"/?page={page-1}", cls="prev") if page > 1 else "",
        A("Next", href=f"/?page={page+1}", cls="next") if page < total_pages else "",
        cls="pagination"
    )

    card = Card(Table(table_header, *table_body, id='todo-list'),
                header=add, footer=pagination_controls),
    ck = (H2("Step 2. Sign Up To Get Updates On LLM Evals "),
          P("You’ll be the first to know about educational materials.  No spam."),
          NotStr('<script async data-uid="a7628dbdca" src="https://hamel.kit.com/a7628dbdca/index.js"></script>')
    )

    footer = Div(
        Footer("made with ", A("fasthtml", href="https://fastht.ml/")),
        cls='footer',
        style='font-size: 0.8em; color: grey; font-style: italic;'
    )

    return Title("AI-Evals"), Main(
        H1("Struggling with LLM Evals?", style="margin-bottom: 5px;"),
        Div("Learn how to do them correctly.", style="font-size: 1em; color: #888; margin-bottom: 20px;"),
        intro,
        H4('LLM Eval Topics', style='text-align: center;'),
        card,
        ck,
        footer,
        cls='container'
    )

@rt("/more")
def more():
    # Load the remaining todos
    sorted_todos = sorted(todos(), key=lambda todo: todo.upvotes or 0, reverse=True)
    remaining_todos = sorted_todos[10:]
    table_body = [todo.__ft__() for todo in remaining_todos]
    return table_body

@rt("/todos/{id}")
def delete(id:int):
    todos.delete(id)
    return clear(id_curr)

@rt("/")
def post(todo:Todo): return todos.insert(todo), mk_input(hx_swap_oob='true')

@rt("/edit/{id}")
def get(id:int):
    res = Form(Group(Input(id="title"), Button("Save")),
        Hidden(id="id"), CheckboxX(id="done", label='Done'),
        hx_put="/", target_id=tid(id), id="edit")
    return fill_form(res, todos.get(id))

@rt("/")
def put(todo: Todo): return todos.upsert(todo), clear(id_curr)

@rt("/todos/{id}")
def get(id:int):
    todo = todos.get(id)
    btn = Button('delete', hx_delete=f'/todos/{todo.id}',
                 target_id=tid(todo.id), hx_swap="outerHTML")
    return Div(Div(todo.title), btn)

@rt("/upvote/{id}")
def upvote(id: int):
    todo = todos.get(id)
    # Initialize upvotes to 0 if it's None
    if todo.upvotes is None:
        todo.upvotes = 0
    todo.upvotes += 1
    todos.upsert(todo)
    # Return a response that triggers a page reload
    return Redirect("/")

serve()