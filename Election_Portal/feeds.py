from django.contrib.syndication.views import Feed
from django.urls import reverse
from Election_Portal.models import Election

class LatestEntriesFeed(Feed):
    title = "News about recent election"
    link = "/sitenews/"
    description = "Updates on recent elections."

    def items(self):
        return Election.objects.order_by('vote_end_time')[:5]

    def item_title(self, item):
        return item.election_name

    def item_description(self, item):
        return item.desc

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return reverse('Election_Portal:index')
