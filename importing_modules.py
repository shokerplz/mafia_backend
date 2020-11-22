from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import random, json, time, threading
import numpy as np
