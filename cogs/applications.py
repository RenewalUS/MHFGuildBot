import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import List
from dotenv import load_dotenv
import os
import asyncio


class applications(commands.Cog, name="applications"):
    load_dotenv()
    
    async def guild_autocomplete(self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        conn = None
        try:
               conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))

               cur = conn.cursor()

               cur.execute("SELECT Name from guilds ORDER BY ID;")
               temp = cur.fetchall()
               choices = [str(element[0]) for element in temp]
              
               cur.close()
               return [
                    app_commands.Choice(name=choice, value=choice)
                    for choice in choices if current.lower() in choice.lower()
               ]
        except (Exception, psycopg2.DatabaseError) as error:
             print(error)

        finally:
             if conn is not None:
                  conn.close()

    
    
    def __init__(self, bot) -> None:
          self.bot = bot
          conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))
          conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
          cursor = conn.cursor()
          cursor.execute(f"LISTEN applications_notification;")

          def handle_notify():
                conn.poll()
                for notify in conn.notifies:
                    print(notify.payload)
                conn.notifies.clear()


          loop = asyncio.get_event_loop()
          loop.add_reader(conn, handle_notify)
          loop.run_forever()

    

          
     
async def setup(bot) -> None:
    await bot.add_cog(applications(bot))
        

    

    
