import abc
import json
from django.shortcuts import render, redirect
from django.urls import path, re_path
from django.views.decorators.cache import cache_control
from django.http import HttpResponse
from django.conf import settings
from typing import List
from .data import *
from .helpers import *


class ProxySource(metaclass=abc.ABCMeta):
    # /proxy/api/:chapter_api_prefix/payload
    @abc.abstractmethod
    def get_chapter_api_prefix(self) -> str:
        raise NotImplementedError

    # /proxy/api/:series_api_prefix/payload
    @abc.abstractmethod
    def get_series_api_prefix(self) -> str:
        raise NotImplementedError

    # /proxy/:reader_prefix/slug
    @abc.abstractmethod
    def get_reader_prefix(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def shortcut_instantiator(self) -> List[re_path]:
        raise NotImplementedError

    @abc.abstractmethod
    def series_api_handler(self, meta_id: str) -> SeriesAPI:
        raise NotImplementedError

    @abc.abstractmethod
    def chapter_api_handler(self, meta_id: str) -> ChapterAPI:
        raise NotImplementedError

    @abc.abstractmethod
    def series_page_handler(self, meta_id: str) -> SeriesPage:
        raise NotImplementedError

    def wrap_chapter_meta(self, meta_id):
        return f"/proxy/api/{self.get_chapter_api_prefix()}/{meta_id}/"

    @cache_control(public=True, max_age=60, s_maxage=60)
    def reader_view(self, request, meta_id, chapter, page=None):
        if page:
            data = self.series_api_handler(meta_id)
            if data:
                data = data.objectify()
                if chapter.replace("-", ".") in data["chapters"]:
                    data["version_query"] = settings.STATIC_VERSION
                    data["relative_url"] = f"proxy/{self.get_reader_prefix()}/{meta_id}"
                    data["api_path"] = f"/proxy/api/{self.get_series_api_prefix()}/"
                    data["reader_modifier"] = f"proxy/{self.get_reader_prefix()}"
                    data["chapter_number"] = chapter.replace("-", ".")
                    return render(request, "reader/reader.html", data)
            return HttpResponse(status=500)
        else:
            return redirect(
                f"reader-{self.get_reader_prefix()}-chapter-page", meta_id, chapter, "1"
            )

    @cache_control(public=True, max_age=60, s_maxage=60)
    def series_view(self, request, meta_id):
        data = self.series_page_handler(meta_id)
        if data:
            data = data.objectify()
            data["version_query"] = settings.STATIC_VERSION
            data["relative_url"] = f"proxy/{self.get_reader_prefix()}/{meta_id}"
            data["reader_modifier"] = f"proxy/{self.get_reader_prefix()}"
            return render(request, "reader/series.html", data)
        else:
            return HttpResponse(status=500)

    @cache_control(public=True, max_age=60, s_maxage=60)
    def series_api_view(self, request, meta_id):
        data = self.series_api_handler(meta_id)
        if data:
            data = data.objectify()
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return HttpResponse(status=500)

    @cache_control(public=True, max_age=60, s_maxage=60)
    def chapter_api_view(self, request, meta_id):
        data = self.chapter_api_handler(meta_id)
        if data:
            data = data.objectify()
            return HttpResponse(
                json.dumps(data["pages"]), content_type="application/json"
            )
        else:
            return HttpResponse(status=500)

    def register_api_routes(self):
        series_prefix = self.get_series_api_prefix()
        chapter_prefix = self.get_chapter_api_prefix()
        routes = []
        if series_prefix:
            routes.append(
                path(
                    f"{series_prefix}/<str:meta_id>/",
                    self.series_api_view,
                    name=f"api-{self.get_reader_prefix()}-series-data",
                )
            )
        if chapter_prefix:
            routes.append(
                path(
                    f"{chapter_prefix}/<str:meta_id>/",
                    self.chapter_api_view,
                    name=f"api-{self.get_reader_prefix()}-chapter-data",
                )
            )
        return routes

    def register_shortcut_routes(self):
        return self.shortcut_instantiator()

    def register_frontend_routes(self):
        return [
            path(
                f"{self.get_reader_prefix()}/<str:meta_id>/",
                self.series_view,
                name=f"reader-{self.get_reader_prefix()}-series-page",
            ),
            path(
                f"{self.get_reader_prefix()}/<str:meta_id>/<str:chapter>/",
                self.reader_view,
                name=f"reader-{self.get_reader_prefix()}-chapter",
            ),
            path(
                f"{self.get_reader_prefix()}/<str:meta_id>/<str:chapter>/<str:page>/",
                self.reader_view,
                name=f"reader-{self.get_reader_prefix()}-chapter-page",
            ),
        ]

