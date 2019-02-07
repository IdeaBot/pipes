from libs import command
# from addons.pipes.libs import pipe
import discord
import re


class Command(command.DirectOnlyCommand):
    '''Inject a message into a pipe

**Usage**
```@Idea <message> >> "<name>" ```
Where
**`<message>`** is the message you want to send
**`<name>`** is the name of the pipe

**Example**
`@Idea Sewage gunk is nasty >> Sewer`
'''

    def matches(self, message):
        return self.collect_args(message) is not None

    def action(self, message):
        real_msg_content = message.content
        args = self.collect_args(message)
        pipe_msg = re.sub(r'<@!?'+self.user().id+r'>', '', args.group(1), re.I).strip()
        print(pipe_msg)
        pipe_name = self.collect_name_args(args.group(2).strip()).group(1)
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
        message.content = real_msg_content

    def collect_args(self, message):
        return re.search(r'(.+)>>(.+)', message.content)

    def collect_name_args(self, string):
        option1 = re.match(r'\"(.+?)\"', string)
        if option1:
            return option1
        return re.match(r'([^\s]+)', string)  # option2
