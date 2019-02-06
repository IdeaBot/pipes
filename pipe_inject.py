from libs import command
# from addons.pipes.libs import pipe
import discord
import re


class Command(command.Command):
    def matches(self, message):
        return self.collect_args(message) is not None

    def action(self, message):
        args = self.collect_args(message)
        pipe_msg = args.group(1).strip()
        pipe_name = args.group(2).strip()
        pipe = self.public_namespace.find_pipe_by_name(pipe_name, self.public_namespace.pipes)
        if pipe is None:
            yield from self.send_message(message.channel, 'Unable to find a pipe named `%s` ' % pipe_name)
            return

        if pipe.perm == pipe.PRIVATE and message.author.id != pipe.owner and message.author.id not in pipe.maintainers:
            yield from self.send_message(message.channel, 'I\'m sorry, only the owner and maintainers of `%s` can inject into this pipe. ' % pipe_name)
            return

        if pipe.mode == pipe.ONEWAY:
            channels = pipe.channels
        elif pipe.mode == pipe.TWOWAY:
            channels = pipe.getAllChannels()
        elif pipe.mode == pipe.THREEWAY:
            yield from self.send_message(message.channel, 'Threeway with a bot? Kinky!')
            return
        else:
            yield from self.send_message(message.channel, 'Pipe `%s` seems to be incorrectly configured. Please contact the devs' % pipe_name)
            return
        message.content = pipe_msg
        args2, kwargs = pipe.gen_message(message)
        for channel_id in channels:
            channel = discord.Object(id=channel_id)
            yield from self.send_message(channel, *args2, **kwargs)

    def collect_args(self, message):
        return re.search(r'(.+)>>(.+)', message.content)
