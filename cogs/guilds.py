import discord
from discord.ext import tasks,commands
from discord import app_commands
from discord.ext.commands import Context
import psycopg2
from dotenv import load_dotenv
import os


class guilds(commands.Cog, name="guilds"):
    load_dotenv()
    
    def __init__(self, bot) -> None:
          self.bot = bot
          self.normal1 = bot.get_channel()
         
          
    @tasks.loop(minutes=1.0)
    async def player_task(self) -> None:
        """
        Setup the game status task of the bot.
        """
        statuses = ["Being Coded", "In Dev.!", "not yet ready"]
        await self.change_presence(activity=discord.Game(random.choice(statuses)))

    @player_task.before_loop
    async def before_player_task(self) -> None:
        """
        Before starting the status changing task, we make sure the bot is ready
        """
        await self.wait_until_ready()

    @commands.hybrid_command(
        name="list",
        description="This command lists all the guilds.",
     )
    async def list(self, context: Context) -> None:
        conn = None
        
        try:
                conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))

                cur = conn.cursor()

                cur.execute("SELECT id,Name from guilds ORDER BY ID;")

                message = "Here is the list of all the guilds:\n"
                
                allguilds = cur.fetchall()
                for param in allguilds:
                    message +=  str(param[0]) + ":" + param[1] + "\n"
                    

                cur.close();  
                embed = discord.Embed(title="list", description=message)
                await context.send(embed=embed)
        except (Exception, psycopg2.DatabaseError) as error:
             print(error)

        finally:
             if conn is not None:
                  conn.close()
    @commands.hybrid_command(
         name="listplayers",
         description="This command lists all characters from a guild"
    )                 
    @app_commands.describe(guildname="the name of the guild you want to list players from")
    async def listplayers(self, context: Context , guildname : str) -> None:
         conn = None
         try:
                conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))
                cur = conn.cursor()
                guildidquery = "SELECT id from guilds where name='" + guildname + "';"
                cur.execute(guildidquery)
                guildid = cur.fetchone()
                if(cur.rowcount == 0):
                     cur.close()
                     errmsg = "No guild with the name " + guildname
                     embed = discord.Embed(title="Error", description=errmsg)
                     await context.send(embed=embed)
                playersquery = "SELECT character_id from guild_characters where guild_id=" + str(guildid[0]) + ";"
                cur.execute(playersquery)
                playeridresult = cur.fetchall()
                playernames = []
                for playerid in playeridresult:
                     idquery = "SELECT name from characters where id=" + str(playerid[0]) + ";"
                     cur.execute(idquery)
                     playernames.append(str(cur.fetchone()[0]))

                mess = "Here are the players currently in guild: " + guildname + "\n"

                for charactername in playernames:
                     mess += str(charactername) + "\n"     

                title = "Players from guild " + guildname
                embed = discord.Embed(title=title, description=mess)
                cur.close()
                await context.send(embed=embed)

         except (Exception , psycopg2.DatabaseError) as error:
              print(error)

         finally:
              if conn is not None:
                   conn.close()

    @commands.hybrid_command(
         name="addtoguild",
         description="This command adds a character to a guild"
    )
    @app_commands.describe(player="The name of the character you want to add.", guildname="the name of the guild you want to add it to")
    async def addcharacter(self, context: Context, player: str, guildname: str) -> None:
         conn = None
         
          
         try:
             conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))
             cur = conn.cursor()
             guildquery = "Select id from guilds where name='" + guildname + "';"
             cur.execute(guildquery)
             guildresult = cur.fetchone()
             if(cur.rowcount == 0):
                  cur.close()
                  errmsg = "No guild with the name " + guildname
                  embed = discord.Embed(title="Error", description=errmsg)
                  await context.send(embed=embed)
 
             guildid = str(guildresult[0])
             playerquery = "SELECT id from characters where name='" + player + "';"
             cur.execute(playerquery)
             playerresult = cur.fetchone()
             if(cur.rowcount == 0):
                  cur.close()
                  errmsg = "No player with the name " + player
                  embed = discord.Embed(title="Error", description=errmsg)
                  await context.send(embed=embed)

             playerid = str(playerresult[0])
             delquery = "DELETE FROM guild_applications where character_id=" + playerid + ";"
             cur.execute(delquery)
             conn.commit()
             addquery = "INSERT INTO guild_characters (guild_id,character_id, order_index) VALUES(" + guildid + "," + playerid + ", (SELECT MAX(order_index) + 1 FROM guild_characters WHERE guild_id =" + guildid + "));"

             cur.execute(addquery)
             conn.commit()
             cur.close()
             mess = "Player " + player + " added to guild " + guildname + " with success"
             embed = discord.Embed(title="add", description=mess)
             await context.send(embed=embed)

         except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    
         finally:
                if conn is not None:
                    conn.close()

    @commands.hybrid_command(
         name="addtoguildbyid",
         description="This command adds a character to a guild"
    )
    @app_commands.describe(id="The id of the character you want to add.", guildname="the name of the guild you want to add it to")
    async def addcharacterbyid(self, context: Context, id: str, guildname: str) -> None:
         
         conn = None
         try:
                conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))
                cur = conn.cursor()
                guildquery = "Select id from guilds where name='" + guildname + "';"
                cur.execute(guildquery)
                guildresult = cur.fetchone()
                if(cur.rowcount == 0):
                     cur.close()
                     errmsg = "No guild with the name " + guildname
                     embed = discord.Embed(title="Error", description=errmsg)
                     await context.send(embed=embed)

                guildid = str(guildresult[0])
                delquery = "DELETE FROM guild_applications where character_id=" + id + ";"
                cur.execute(delquery)
                conn.commit()
                addquery = "INSERT INTO guild_characters (guild_id,character_id, order_index) VALUES(" + guildid + "," + id + ", (SELECT MAX(order_index) + 1 FROM guild_characters WHERE guild_id =" + guildid + "));"

                cur.execute(addquery)
                conn.commit()
                cur.close()
                mess = "Character id " + id + " added to guild " + guildname + " with success"
                embed = discord.Embed(title="add", description=mess)
                await context.send(embed=embed)

         except (Exception, psycopg2.DatabaseError) as error:
              print(error)
        
         finally:
                if conn is not None:
                    conn.close()

    @commands.hybrid_command(
            name="remove",
            description="This command removes a character from a guild"
        )
    @app_commands.describe(player="The name of the character you want to remove.", guildname="the name of the guild you want to remove it from")
    async def addplayer(self, context: Context, player: str, guildname: str) -> None:
            
            conn = None
            try:
                    conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))
                    cur = conn.cursor()
                    guildquery = "Select id from guilds where name='" + guildname + "';"
                    cur.execute(guildquery)
                    guildresult = cur.fetchone()
                    if(cur.rowcount == 0):
                        cur.close()
                        errmsg = "No guild with the name " + guildname
                        embed = discord.Embed(title="Error", description=errmsg)
                        await context.send(embed=embed)

                    guildid = str(guildresult[0])
                    playerquery = "SELECT id from characters where name='" + player + "';"
                    cur.execute(playerquery)
                    playerresult = cur.fetchall()
                    if(cur.rowcount == 0):
                        cur.close()
                        errmsg = "No player with the name " + player
                        embed = discord.Embed(title="Error", description=errmsg)
                        await context.send(embed=embed)
                    guildplayerid = 0
                    for testplayerid in playerresult:
                          queryplayerid = "SELECT character_id from guild_characters where character_id=" + str(testplayerid[0]) + " AND guild_id=" + str(guildid) + ";"
                          cur.execute(queryplayerid)
                          if(cur.rowcount > 0):
                                guildplayerid = testplayerid[0]
                             
                    if(guildplayerid == 0):
                        cur.close()
                        errmsg = "No player with the name " + player + " in the guild " + guildname 
                        embed = discord.Embed(title="Error", description=errmsg)
                        await context.send(embed=embed)

                    removequery = "DELETE FROM guild_characters where guild_id=" + str(guildid) + " AND character_id=" + str(guildplayerid) + ";"

                    cur.execute(removequery)
                    conn.commit()
                    cur.close()
                    mess = "Player " + player + " removed from guild" + guildname + " with success"
                    embed = discord.Embed(title="add", description=mess)
                    await context.send(embed=embed)

            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            
            finally:
                    if conn is not None:
                        conn.close()

    @commands.hybrid_command(
              name="flushapplications",
              description="Removes all applications"
    )                    
    async def flushapplications(self, context: Context) -> None:
               conn = None
               try:
                     conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))
                     cur = conn.cursor()
                     appquery = "Delete from guild_applications;"
                     cur.execute(appquery)
                     conn.commit()
                     msg = "All applications removed with success"  
                     embed = discord.Embed(title="Success", description=msg)
                     await context.send(embed=embed)

               except(Exception, psycopg2.DatabaseError) as error:
                     print(error)
               
               finally:
                     if conn is not None:
                           conn.close()

     
    @commands.hybrid_command(
              name="flushapplicationbyid",
              description="Removes an application from a character"
    )
    @app_commands.describe(id="the id of the character you want to remove application for ")
    async def flushapplicationbyid(self, context: Context, id : str) -> None:
               conn = None
               try:
                     conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))
                     cur = conn.cursor()
                     appquery = "Delete from guild_applications where character_id=" + id + ";"
                     cur.execute(appquery)
                     conn.commit()
                     msg = "Application for character id " + id + " removed with success."  
                     embed = discord.Embed(title="Success", description=msg)
                     await context.send(embed=embed)

               except(Exception, psycopg2.DatabaseError) as error:
                     print(error)
               
               finally:
                     if conn is not None:
                           conn.close()

    @commands.hybrid_command(
              name="flushapplicationbyname",
              description="Removes an application from a character"
    )
    @app_commands.describe(name="the name of the character you want to flush application for ")
    async def flushapplicationbyname(self, context: Context, name : str) -> None:
               conn = None
               try:
                     conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))
                     cur = conn.cursor()
                     characterquery = "select id from characters where name='" + name + "';"
                     cur.execute(characterquery)
                     if(cur.rowcount == 0):
                         cur.close()
                         conn.close()
                         errmsg = "No character with the name " + name
                         embed = discord.Embed(title="Error", description=errmsg)
                         await context.send(embed=embed)

                     id = cur.fetchone()
                     appquery = "Delete from guild_applications where character_id=" + id[0] + ";"
                     cur.execute(appquery)
                     conn.commit()
                     msg = "Application for character name " + name + " removed with success."  
                     embed = discord.Embed(title="Success", description=msg)
                     await context.send(embed=embed)

               except(Exception, psycopg2.DatabaseError) as error:
                     print(error)
               
               finally:
                     if conn is not None:
                           conn.close()
    @commands.hybrid_command(
                name="leader",
                description="This command gives the leader of a guild"
            )
    @app_commands.describe( guildname="the name of the guild you want to know the leader of")
    async def leader(self, context: Context, guildname: str) -> None:
                conn = None
                try:
                        conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))
                        cur = conn.cursor()
                        guildquery = "Select leader_id from guilds where name=" + guildname + ";"
                        cur.execute(guildquery)
                        guildresult = cur.fetchone()
                        if(cur.rowcount == 0):
                            cur.close()
                            errmsg = "No guild with the name " + guildname
                            embed = discord.Embed(title="Error", description=errmsg)
                            await context.send(embed=embed)

                        leaderid = str(guildresult[0])
                        playerquery = "SELECT id from characters where name=" + leaderid + ";"
                        cur.execute(playerquery)
                        playerresult = cur.fetchone()
                        if(cur.rowcount == 0):
                            cur.close()
                            errmsg = "No player with the name " + player
                            embed = discord.Embed(title="Error", description=errmsg)
                            await context.send(embed=embed)
                            
                        playerid = str(playerresult[0])

                        removequery = "DELETE FROM guild_characters where guild_id=" + guildid + " AND player_id=" + playerid + ";"

                        cur.execute(removequery)

                        cur.close()
                        mess = "Player " + player + " removed from guild" + guildname + " with success"
                        embed = discord.Embed(title="add", description=mess)
                        await context.send(embed=embed)

                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                
                finally:
                        if conn is not None:
                            conn.close()
    @commands.hybrid_command(
              name="resetloginboost",
              description="Resets the login boost from a character"
     )
    @app_commands.describe(name="the name of the character you want to reset the login boost  for ")
    async def resetloginboost(self, context: Context, name : str) -> None:
          
               conn = None
               try:
                     conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))
                     cur = conn.cursor()
                     characterquery = "select id from characters where name='" + name + "';"
                     cur.execute(characterquery)
                     if(cur.rowcount == 0):
                         cur.close()
                         conn.close()
                         errmsg = "No character with the name " + name
                         embed = discord.Embed(title="Error", description=errmsg)
                         await context.send(embed=embed)

                     
                     appquery = "UPDATE public.characters SET boost_time = NULL WHERE id = (SELECT id FROM public.characters WHERE name = '"+ name + "');"
                     cur.execute(appquery)
                     conn.commit()
                     msg = "Login boost reset for character " + name + "."  
                     embed = discord.Embed(title="Success", description=msg)
                     await context.send(embed=embed)

               except(Exception, psycopg2.DatabaseError) as error:
                     print(error)
               
               finally:
                     if conn is not None:
                           conn.close()
    @commands.hybrid_command(
         name="listguilds",
         description="This command lists all the guilds"
    )                 
    @app_commands.describe()
    async def listguilds(self, context: Context) -> None:
         
         conn = None
         try:
                conn = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),user=os.getenv("USER"),password=os.getenv("PASSWORD"))
                cur = conn.cursor()
                guildquery = "SELECT name from guilds;"
                cur.execute(guildquery)
                guilds = cur.fetchall()
                if(cur.rowcount == 0):
                     cur.close()
                     errmsg = "No guilds found!"
                     embed = discord.Embed(title="Error", description=errmsg)
                     await context.send(embed=embed)

                mess = "Here are the current guilds:\n"

                for guildname in guilds:
                     mess += str(guildname[0]) + "\n"     

                title = "List of all current guilds "
                embed = discord.Embed(title=title, description=mess)
                cur.close()
                await context.send(embed=embed)

         except (Exception , psycopg2.DatabaseError) as error:
              print(error)

         finally:
              if conn is not None:
                   conn.close()
async def setup(bot) -> None:
    await bot.add_cog(guilds(bot))
        

    

    
