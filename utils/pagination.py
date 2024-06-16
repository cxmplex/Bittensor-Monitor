import discord
from discord.ui import View, Button

class PaginatorView(View):
    def __init__(self, pages):
        super().__init__(timeout=None)
        self.pages = pages
        self.current_page = 0

        self.next_button = Button(label="Next", style=discord.ButtonStyle.primary)
        self.prev_button = Button(label="Previous", style=discord.ButtonStyle.primary)

        self.next_button.callback = self.next_page
        self.prev_button.callback = self.prev_page

        self.add_item(self.prev_button)
        self.add_item(self.next_button)

        self.prev_button.disabled = True
        if len(self.pages) == 1:
            self.next_button.disabled = True

    async def update_message(self, interaction):
        await interaction.response.edit_message(content=self.pages[self.current_page], view=self)
    
    async def next_page(self, interaction):
        self.current_page += 1
        if self.current_page == len(self.pages) - 1:
            self.next_button.disabled = True
        self.prev_button.disabled = False
        await self.update_message(interaction)

    async def prev_page(self, interaction):
        self.current_page -= 1
        if self.current_page == 0:
            self.prev_button.disabled = True
        self.next_button.disabled = False
        await self.update_message(interaction)

async def paginate(ctx, pages):
    view = PaginatorView(pages)
    await ctx.send(content=pages[0], view=view)

