from services.email_agent.graph import WorkFlow

app = WorkFlow().app
app.invoke({})