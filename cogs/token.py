# Made By DarkNighT (- mmiiiuu)
# Made By DarkNighT (- mmiiiuu)
# Made By DarkNighT (- mmiiiuu)

import discord
from discord import ui
import sqlite3
from discord.ext import commands

class TokenModal(discord.ui.Modal, title="Link Discord Token"):
    token_input = discord.ui.TextInput(label="Enter Your Discord User Token", placeholder="Your user token...", required=True, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute('REPLACE INTO token (user_id, token) VALUES (?, ?)', (str(interaction.user.id), self.token_input.value))
        conn.commit()
        conn.close()
        await interaction.response.send_message("✅ Token linked! Use `!quests`", ephemeral=True)
        
class Script(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Android", value="android"),
            discord.SelectOption(label="IOS", value="ios"),
        ]
        super().__init__(placeholder="Select your platform", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        platform = self.values[0]
        script_content = ""
        
        if platform == "android":
            script_content = """```js\njavascript:(function(){try{let f=document.createElement('iframe');document.body.appendChild(f);let t=JSON.parse(f.contentWindow.localStorage.token);let ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();let n=document.createElement('div');n.innerHTML='<strong>sawof</strong><br>Your Account T0k8n Has Copied Successfully';n.style.cssText='position:fixed;top:20px;left:20px;background:#001f3f;color:#7FDBFF;padding:12px 16px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.4);font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;font-size:14px;z-index:99999;opacity:0;transition:opacity 0.3s ease-in-out;';document.body.appendChild(n);setTimeout(()=>{n.style.opacity='1';},50);setTimeout(()=>{n.style.opacity='0';setTimeout(()=>n.remove(),500);},3500);}catch(e){alert('Error copying token');}})();\n```"""        
        elif platform == "ios":
            script_content = """```js\njavascript:(function(){try{var i=document.createElement('iframe');i.style.display='none';document.body.appendChild(i);var t=i.contentWindow.localStorage.token.replace(/^"(.*)"$/, '$1');navigator.clipboard.writeText(t).then(function(){var d=document.createElement('div');d.innerHTML='<strong>%C2%A9%EF%B8%8F sawof</strong><br>Your token copied successfully';Object.assign(d.style,{position:'fixed',top:'10px',left:'10px',background:'#d4edda',color:'#155724',padding:'10px',border:'1px%20solid%20#c3e6cb',borderRadius:'5px',zIndex:9999,fontFamily:'sans-serif'});document.body.appendChild(d);setTimeout(()=%3Ed.remove(),3000);});}catch(e){alert('Failed%20to%20copy%20token:%20'+e);}})();\n```"""        
        
        v = ui.LayoutView(timeout=None)
        c = ui.Container(
            ui.TextDisplay(f"### {platform.upper()} Token Script"),
            ui.Separator(),
            ui.TextDisplay(f"{script_content}") 
        ) 
        v.add_item(c)
        await interaction.response.send_message(view=v, ephemeral=True)
        

        
class LinkView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)
    c = ui.Container(
        ui.TextDisplay("### Link Your Account"),
        ui.Separator(),
        ui.TextDisplay("**Terms & Privacy**\n\n> By linking your Discord User Token, you agree to our terms of service and privacy policy.\n> Your token is securely stored and used only for quest completion.\n> We do not store or share your token with any third parties.\n> Use at your own risk.\n\n**How to get your token?**\n> Use `.script` command to get instructions.")
    )
    r = ui.ActionRow()    
    @r.button(label="Token", style=discord.ButtonStyle.primary)
    async def link_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TokenModal())
        
        
class TokenCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.command(name='link')
    async def link(self, ctx):
        view = LinkView()
        await ctx.send(view=view)
        
    @commands.command(name='unlink')
    async def unlink(self, ctx):
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute('SELECT token FROM token WHERE user_id = ?', (str(ctx.author.id),))
        result = cursor.fetchone()
        if not result:
            await ctx.send("❌ You don't have a linked token.")
            conn.close()
            return
        cursor.execute('DELETE FROM token WHERE user_id = ?', (str(ctx.author.id),))
        conn.commit()
        conn.close()
        await ctx.send("✅ Token unlinked successfully.")
        
    @commands.command(name='script')
    async def script(self, ctx):
        file =  discord.File("video.mp4")
        gallery = discord.ui.MediaGallery(
            discord.MediaGalleryItem(file, description="How to get your token")
        )
        v = ui.LayoutView(timeout=None)
        c = ui.Container(
            ui.TextDisplay("### How to Get Your Token"),
            ui.Separator(),
            gallery,
            ui.TextDisplay("Select your platform below to get the script.")
        )
        r = ui.ActionRow()
        r.add_item(Script())
        v.add_item(c)
        v.add_item(r)
        await ctx.send(view=v, files=[file])
        
        
async def setup(bot):
    await bot.add_cog(TokenCog(bot))
