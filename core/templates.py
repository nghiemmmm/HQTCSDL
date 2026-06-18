from fastapi.templating import Jinja2Templates as FastAPIJinja2Templates


class Jinja2Templates(FastAPIJinja2Templates):
    def TemplateResponse(self, *args, **kwargs):
        if len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], dict):
            name = args[0]
            context = args[1]
            request = context.get("request")
            return super().TemplateResponse(request, name, context, **kwargs)

        return super().TemplateResponse(*args, **kwargs)
