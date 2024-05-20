import discord
from discord.ext import commands,tasks
from discord import app_commands
from discord.ext.commands import Context
import psycopg2
from dotenv import load_dotenv
import os

class Applications(commands.Cog, name="applications"):
    load_dotenv()
    
    
    def __init__(self, bot) -> None:
          self.bot = bot
          self.conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))
          self.application_task.start()
                        

    @tasks.loop(seconds=1.0)
    async def application_task(self) -> None:
            self.conn.poll()
            for notify in self.conn.notifies:
                    cursor = self.conn.cursor()
                    cursor.execute(f"Select guild_id,character_id from guild_applications where id={notify.payload}")
                    result = cursor.fetchone()
                    
                    cursor.execute(f"Select name,leader_id from guilds where id = {result[0]}")
                    guildnameresult = cursor.fetchone()
                    
                    cursor.execute(f"SELECT name,hr,gr from characters where id={result[1]}")
                    applicantname = cursor.fetchone()

                    cursor.execute(f"SELECT user_id from characters where id={guildnameresult[1]}")
                    leadercharacterid = cursor.fetchone()

                    cursor.execute(f"SELECT discord_id from users where id={leadercharacterid[0]}")
                    leaderdiscordid = cursor.fetchone()



                    message = f"Player {applicantname[0]} (id:{result[1]} , HR:{applicantname[1]}, GR:{applicantname[2]}) wants to join guild {guildnameresult[0]}.\n"
                    
                    if(leaderdiscordid[0] is not None):
                          message += f"<@{leaderdiscordid[0]}>," 
                    message += f"please use /accept {notify.payload} or /decline {notify.payload} command."
                    embed = discord.Embed(title=f"New Application: {applicantname[0]} (id:{result[1]})", description=message)
                    channel = self.bot.get_channel(int(os.getenv("APPLICATIONCHANNEL")))
                    await channel.send(embed=embed)
                    print(notify.payload)
            self.conn.notifies.clear()
    


    async def preparenotify(self) -> None :
          await self.bot.wait_until_ready()
          cursor = self.conn.cursor()
          cursor.execute(f"CREATE OR REPLACE FUNCTION notify_new_application() RETURNS trigger AS $$
                         BEGIN
                         PERFORM pg_notify('applications_notification', NEW.id::text);
                         RETURN NEW;
                         END;
                         $$ LANGUAGE plpgsql;
                         CREATE OR REPLACE TRIGGER application_notify_trigger
                         AFTER INSERT ON guild_applications
                         FOR EACH ROW EXECUTE PROCEDURE notify_new_application();")
          self.conn.commit()
          print("Added or replaced trigger successful")
          return None

    @application_task.before_loop
    async def before_status_task(self) -> None:
        """
        Before starting the status changing task, we make sure the bot is ready
        """
        await self.bot.wait_until_ready()
        await self.preparenotify(self)
        print("ready to listen") 
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = self.conn.cursor()
        cursor.execute(f"LISTEN applications_notification;")



    @commands.hybrid_command(
         name="accept",
         description="This command accepts an application to your guild."
    )
    @app_commands.describe(id="The number given in the message")
    async def accept(self, context: Context, id: str) -> None:
         try:
                cur = self.conn.cursor()
                guildquery = f"Select guild_id,character_id from guild_applications where id={id}"
                cur.execute(guildquery)
                guildresult = cur.fetchone()
                if(cur.rowcount == 0):
                     errmsg = "application linked with id: " + id
                     embed = discord.Embed(title="Error", description=errmsg)
                     await context.send(embed=embed)

                

                guildid = str(guildresult[0])    
                
                cur.execute(f"SELECT leader_id,name from guilds where id = {guildid}")
                leaderid = cur.fetchone()
                cur.execute(f"SELECT user_id from characters where id={leaderid[0]}")
                leaderuserid = cur.fetchone()
                cur.execute(f"SELECT discord_id from users where id={leaderuserid[0]}")
                leaderdiscordid = cur.fetchone()
               
                if(str(leaderdiscordid[0]) != str(context.author.id)):
                            print(context.author.id)
                            errmsg = f"you're not the leader of the guild {leaderid[1]}."
                            embed = discord.Embed(title="Error", description=errmsg)
                            await context.send(embed=embed)

                
                delquery = "DELETE FROM guild_applications where id=" + id + ";"
                cur.execute(delquery)
                self.conn.commit()
                addquery = "INSERT INTO guild_characters (guild_id,character_id, order_index) VALUES(" + guildid + "," + str(guildresult[1]) + ", (SELECT MAX(order_index) + 1 FROM guild_characters WHERE guild_id =" + guildid + "));"

                cur.execute(addquery)
                self.conn.commit()
                mess = "Application " + id + " accepted with success"
                embed = discord.Embed(title="Accepted", description=mess)
                await context.send(embed=embed)

         except (Exception, psycopg2.DatabaseError) as error:
              print(error)
       
    @commands.hybrid_command(
        name="decline",
        description="This command declines an application to your guild."
        )
    @app_commands.describe(id="The number given in the message")
    async def decline(self, context: Context, id: str) -> None:
        try:
                cur = self.conn.cursor()
                guildquery = f"Select guild_id,character_id from guild_applications where id={id}"
                cur.execute(guildquery)
                guildresult = cur.fetchone()
                if(cur.rowcount == 0):
                     errmsg = "application linked with id: " + id
                     embed = discord.Embed(title="Error", description=errmsg)
                     await context.send(embed=embed)

                

                guildid = str(guildresult[0])    
                
                cur.execute(f"SELECT leader_id,name from guilds where id = {guildid}")
                leaderid = cur.fetchone()
                cur.execute(f"SELECT user_id from characters where id={leaderid[0]}")
                leaderuserid = cur.fetchone()
                cur.execute(f"SELECT discord_id from users where id={leaderuserid[0]}")
                leaderdiscordid = cur.fetchone()
               
                if(str(leaderdiscordid[0]) != str(context.author.id)):
                            print(context.author.id)
                            errmsg = f"you're not the leader of the guild {leaderid[1]}."
                            embed = discord.Embed(title="Error", description=errmsg)
                            await context.send(embed=embed)

                
                delquery = "DELETE FROM guild_applications where id=" + id + ";"
                cur.execute(delquery)
                self.conn.commit()
                mess = "Application " + id + " Declined with success"
                embed = discord.Embed(title="Declined", description=mess)
                await context.send(embed=embed)

        except (Exception, psycopg2.DatabaseError) as error:
              print(error)

          
     
async def setup(bot) -> None:
    await bot.add_cog(Applications(bot))
        

    

    
