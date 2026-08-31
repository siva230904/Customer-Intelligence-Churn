from fastapi import FastAPI


from database import Base,engine
from routes.churnroutes import router
Base.metadata.create_all(bind=engine)



app=FastAPI()

app.include_router(router=router)


