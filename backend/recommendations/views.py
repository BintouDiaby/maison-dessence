
from django.http import JsonResponse, Http404
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .recommender import train, similar_products


class TrainRecommenderView(APIView):
	"""Train the recommender. Restricted to admin users (JWT / IsAdminUser).

	The management command `train_recommender` remains available for CLI usage.
	"""
	permission_classes = [IsAdminUser]

	def post(self, request):
		res = train()
		return Response(res, status=status.HTTP_200_OK)


class DemoView(APIView):
	"""Serve a tiny HTML demo that calls the recommender API via fetch."""
	permission_classes = []  # public demo

	def get(self, request):
		return render(request, 'recommendations/demo.html', {})


class SimilarProductsView(APIView):
	permission_classes = []

	def get(self, request, product_id):
		try:
			k = int(request.GET.get('k', 5))
		except Exception:
			k = 5
		sims = similar_products(product_id, k=k)
		if sims is None:
			raise Http404('No recommendations')
		return Response({'product_id': product_id, 'similar': sims})
