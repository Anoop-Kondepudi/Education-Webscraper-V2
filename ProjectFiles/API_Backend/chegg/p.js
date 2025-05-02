// p.js
const { Client, Intents, MessageActionRow, Modal, TextInputComponent } = require('discord.js');
const discordModals = require('discord-modals');
const fs = require('fs');

const client = new Client({
  intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES],
});

discordModals(client);

client.once('ready', async () => {
  console.log('Bot is ready!');
  const guildId = '1236810621731733624'; // Your guild ID
  const guild = client.guilds.cache.get(guildId);
  if (!guild) return console.warn('Guild not found. Check your guild ID.');

  try {
    await guild.commands.create({
      name: 'input-cookie',
      description: 'Input your cookie information',
    });
    console.log('Slash command registered.');
  } catch (error) {
    console.error('Error registering the slash command:', error);
  }
});

client.on('interactionCreate', async (interaction) => {
  if (interaction.isCommand() && interaction.commandName === 'input-cookie') {
    const modal = new Modal()
      .setCustomId('inputCookieModal')
      .setTitle('Cookie Input')
      .addComponents(
        new MessageActionRow().addComponents(
          new TextInputComponent()
            .setCustomId('cookieInput')
            .setLabel('Enter your cookie here')
            .setStyle('PARAGRAPH')
            .setRequired(true)
        )
      );

    await interaction.showModal(modal);
  }
});

client.on('modalSubmit', async (modal) => {
  if (modal.customId === 'inputCookieModal') {
    try {
      const cookieValue = modal.components[0].components[0].value;
      fs.writeFileSync('cookie.txt', cookieValue + '\n', { flag: 'a' });
      await modal.reply({ content: 'Cookie saved! Restarting...', ephemeral: true });

      // Terminate the process after a short delay
      setTimeout(() => process.exit(0), 1000);
    } catch (error) {
      console.error('Error handling modal submission:', error);
      await modal.reply({ content: 'An error occurred.', ephemeral: true });
    }
  }
});

module.exports = client;
