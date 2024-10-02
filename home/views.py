from .models import BlogPost
from django.http import JsonResponse
from .models import PredictionResponse
from .forms import CommentForm
from django.shortcuts import render, get_object_or_404, redirect
import os
import pandas as pd
import plotly.graph_objs as go
from django.conf import settings

# Load the dataset file path from your media or static folder
DATA_FILE_PATH = os.path.join(settings.BASE_DIR, 'home/static/data/life-expectancy-at-birth-including-the-un-projections.csv')

def get_climate_factors(request):
    nuclear_factor = int(request.GET.get('nuclear_factor'))
    
    # Filter scenarios_df for rows where the nuclear factor matches the one from the request
    valid_climate_factors = scenarios_df[scenarios_df['nuclear_factor'] == nuclear_factor]['climate_factor'].unique()
    
    # Return the valid climate factors as a JSON response
    return JsonResponse({
        'valid_factors': list(valid_climate_factors)
    })

# Load life expectancy data
life_expectancy_data = pd.read_csv(DATA_FILE_PATH)

# Define scenarios dataframe
scenarios_df = pd.DataFrame({
    "nuclear_factor": [1, 1, 1, 1, 1, 2, 3, 4, 5],
    "climate_factor": [1, 2, 3, 4, 5, 1, 1, 1, 1],
    "life_exp": [80.9, 80.5, 80.1, 79.9, 78.9, 78.4, 68.2, 55.9, 46.5],
    "description": [
        "Mild impact on both nuclear and climate fronts, minimal disruption expected.",
        "Mild nuclear impact with moderate climate change, increased environmental stress.",
        "Mild nuclear impact with severe climate change, substantial risk to health infrastructure.",
        "Mild nuclear impact with extreme climate events, critical risks to public health.",
        "Mild nuclear impact with catastrophic climate effects, widespread existential threats.",
        "Moderate nuclear impact with mild climate change, noticeable environmental effects.",
        "Significant nuclear impact, potential for regional instability.",
        "Severe nuclear degradation, high probability of societal collapse.",
        "Catastrophic nuclear fallout, survival of human habitats severely threatened."
    ]
})

def homepage(request):
    countries = life_expectancy_data['Country'].unique()
    
    # Default to the first country or use the one selected by the user
    selected_country = request.GET.get('country', countries[0])
    nuclear_factor = int(request.GET.get('nuclear_factor', 1))
    climate_factor = int(request.GET.get('climate_factor', 1))

    # Filter data for the selected country
    country_data = life_expectancy_data[life_expectancy_data['Country'] == selected_country]

    # Get the scenario based on the nuclear and climate factor
    scenario = scenarios_df[(scenarios_df['nuclear_factor'] == nuclear_factor) & 
                            (scenarios_df['climate_factor'] == climate_factor)].iloc[0]

    # Get the 2021 life expectancy
    life_exp_2021 = country_data[country_data['Year'] == 2021]['Life Expectancy'].values[0]

    # Generate future projections based on the scenario
    years = list(range(2021, 2101))
    life_exp_projections = [life_exp_2021 + (scenario['life_exp'] - life_exp_2021) * (year - 2021) / (2100 - 2021) for year in years]

    # Create a Plotly figure
    fig = go.Figure()

    # Plot historical data
    historical_data = country_data[country_data['Year'] <= 2021]
    fig.add_trace(go.Scatter(x=historical_data['Year'], y=historical_data['Life Expectancy'], mode='lines+markers', name='Historical'))

    # Plot future projections based on nuclear and climate factors
    fig.add_trace(go.Scatter(x=years, y=life_exp_projections, mode='lines+markers', name='Future Projections by Factors'))

    # Update the layout of the plot
    fig.update_layout(
        title=f'Life Expectancy Projection for {selected_country}',
        xaxis_title='Year',
        yaxis_title='Life Expectancy (years)'
    )

    # Convert the plot to an HTML element
    plot_div = fig.to_html(full_html=False)

    context = {
        'plot_div': plot_div,
        'countries': countries,
        'selected_country': selected_country,
        'nuclear_factor': nuclear_factor,
        'climate_factor': climate_factor,
        'scenario_description': scenario['description'],
        'factor_range': range(1, 6)  # To generate the options for factors
    }

    return render(request, 'home/homepage.html', context)


def blog_list(request):
    posts = BlogPost.objects.all().order_by('-date')
    return render(request, 'home/blog_list.html', {'posts': posts})

def blog_detail(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    
    # Increment views count
    post.views += 1
    post.save()

    comments = post.comments.all()
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('blog_detail', post_id=post.id)

    return render(request, 'home/blog_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })


# Handle the like (heart) functionality
def like_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    post.likes += 1
    post.save()
    return redirect('blog_detail', post_id=post.id)

QUESTIONS = [
    {"id": 1, "text": "Will the temperature in your hometown be warmer, cooler, or the same on average this summer compared to last year?", "choices": ["Cooler", "Warmer", "Same"]},
    {"id": 2, "text": "Will the school or university you attend commit to becoming carbon neutral by 2030?", "choices": ["Yes", "No"]},
    {"id": 3, "text": "Will you or someone you know switch to an electric or hybrid vehicle within the next 5 years?", "choices": ["Yes", "No"]},
    {"id": 4, "text": "Will we see the first carbon-neutral city by 2040?", "choices": ["Yes", "No"]},
    {"id": 5, "text": "Will the use of single-use plastics (such as straws, cups, and bags) decrease by 50% in your school or workplace by the end of this year?", "choices": ["Yes", "No"]},
    {"id": 6, "text": "Will a global carbon tax be implemented in the next 15 years?", "choices": ["Yes", "No"]},
    {"id": 7, "text": "By what percentage will carbon dioxide emissions increase or decrease globally from 2020 to 2025", "choices": ["-25%", "-20%", "-15%", "-10%", "-5%", "0%", "5%", "10%", "15%", "20%", "25%"]},
    {"id": 8, "text": "In the next century will temperatures increase by…", "choices": ["Less than 2 degrees", "Less than 4 degrees", "Less than 6 degrees", "More than 6 degrees"]},
    {"id": 9, "text": "Will renewable energy sources account for more than 50% of global energy production by the year 2050?", "choices": ["Yes", "No"]},
    {"id": 10, "text": "Will the city where you live install more bike lanes or pedestrian walkways over the next 2 years to encourage low-carbon transportation?", "choices": ["Yes", "No"]},
    {"id": 11, "text": "What is the percent probability of Russia and the US going into nuclear war in the next 1 year?", "choices": ["-25%", "-20%", "-15%", "-10%", "-5%", "0%", "5%", "10%", "15%", "20%", "25%"]},
    {"id": 12, "text": "What is the percent probability of the US and China going into nuclear war in the next 1 year?", "choices": ["-25%", "-20%", "-15%", "-10%", "-5%", "0%", "5%", "10%", "15%", "20%", "25%"]},
    {"id": 13, "text": "What is the percent probability of the US and China going into nuclear war in the next 10 years?", "choices": ["-25%", "-20%", "-15%", "-10%", "-5%", "0%", "5%", "10%", "15%", "20%", "25%"]},
    {"id": 14, "text": "What is the percent probability of Russia and Ukraine going into nuclear war in the next 1 year?", "choices": ["-25%", "-20%", "-15%", "-10%", "-5%", "0%", "5%", "10%", "15%", "20%", "25%"]},
    {"id": 15, "text": "What is the percent probability of Russia and Ukraine going into nuclear war in the next 10 years?", "choices": ["-25%", "-20%", "-15%", "-10%", "-5%", "0%", "5%", "10%", "15%", "20%", "25%"]},
    {"id": 16, "text": "What is the percent probability of Russia and the US going into nuclear war in the next 10 years?", "choices": ["-25%", "-20%", "-15%", "-10%", "-5%", "0%", "5%", "10%", "15%", "20%", "25%"]},
    {"id": 17, "text": "Will the Russia-Ukraine conflict lead to at least one nuclear detonation in the next...?", "choices": ["Yes", "No"]},
    {"id": 18, "text": "By 2040 will there be more nuclear weapons in the world than in 2022?", "choices": ["Yes", "No"]},
    {"id": 19, "text": "Before 2024, will a nuclear device be detonated somewhere in the world?", "choices": ["Yes", "No"]},
    {"id": 20, "text": "Will there be complete nuclear disarmament (zero functional nuclear weapons) by 2100?", "choices": ["Yes", "No"]},
    {"id": 21, "text": "Will human life expectancy in 2025 be higher or lower than in 2023?", "choices": ["Higher", "Lower"]},
    {"id": 22, "text": "Will human life expectancy in 2050 be higher or lower than in 2023?", "choices": ["Higher", "Lower"]},
    {"id": 23, "text": "Will human life expectancy in 2100 be higher or lower than in 2023?", "choices": ["Higher", "Lower"]},
    {"id": 24, "text": "What is the percent probability of a successful nuclear disarmament treaty being signed by at least 2 major nuclear powers (Russia, US, China) in the next five years?", "choices": ["-25%", "-20%", "-15%", "-10%", "-5%", "0%", "5%", "10%", "15%", "20%", "25%"]},
]


def prediction_market(request):
    if request.method == "GET":
        return render(request, 'home/prediction_market.html', {'questions': QUESTIONS})

def submit_answer(request):
    if request.method == "POST":
        question_id = request.POST.get('question_id')  # Capture the question ID
        answer = request.POST.get('answer')
        user = request.POST.get('user') or "Anonymous"
        
        if not question_id:
            return JsonResponse({'error': 'Question ID is missing'}, status=400)
        
        # Store the user's answer
        PredictionResponse.objects.create(
            question_number=int(question_id),  # Ensure the question_id is passed as an integer
            user=user,
            answer=answer
        )
        
        # Find the next question
        next_question_id = int(question_id) + 1
        if next_question_id <= len(QUESTIONS):
            next_question = QUESTIONS[next_question_id - 1]
            return JsonResponse({'next_question': next_question})
        else:
            return JsonResponse({'finished': True})

    return JsonResponse({'error': 'Invalid request'}, status=400)
