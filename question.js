// Base code from webdevtrick (https://webdevtrick.com)
// addr of server

var server_addr_request_scores;
var server_addr_reset_scores;

//initialised team score at end of every question
function initTeamSCore()
{
    // reset on server
    fetch(server_addr_reset_scores)
      .then((response) => {
        return response.text();
      })
}

function Quiz(questions) {
    this.score = 0;
    this.questions = questions;
    this.questionIndex = 0;
}
 
Quiz.prototype.getQuestionIndex = function() {
    return this.questions[this.questionIndex];
}
 
Quiz.prototype.guess = function(answer) {
    if(this.getQuestionIndex().isCorrectAnswer(answer)) {
        this.score++;
    }
 
    this.questionIndex++;
}
 
Quiz.prototype.isEnded = function() {
    return this.questionIndex === this.questions.length;
}
 
 
function Question(module, text, choices, answer) {
    this.module = module;
    this.text = text;
    this.choices = choices;
    this.answer = answer;
}
 
Question.prototype.isCorrectAnswer = function(choice) {
    return this.answer === choice;
}
 
 
function populate(quiz) {
    if(quiz.isEnded()) {
        showScores(quiz);
    }
    else {
        // show next question
        var element = document.getElementById("question");
        element.innerHTML = quiz.getQuestionIndex().text;
 
        // show options
        var choices = quiz.getQuestionIndex().choices;
        for(var i = 0; i < choices.length; i++) {
            var element = document.getElementById("choice" + i);
            element.innerHTML = choices[i];
            guess(quiz, "btn" + i, choices[i]);
        }
        var choice_correct = document.getElementById("check_correct");
        choice_correct.innerHTML = "Check answer";
        var btn_correct = document.getElementById("btn_correct");
        btn_correct.onclick = function() 
        {
            ans = quiz.getQuestionIndex().answer;
            console.log(ans);
            choice_correct.innerHTML = ans;
        }
        
        initTeamSCore();
        showProgress(quiz);
    }
};
 
function guess(quiz, id, guessVal) {
    var button = document.getElementById(id);
    button.onclick = function() {
        quiz.guess(guessVal);
        populate(quiz);
    }
};
 
 
function showProgress(quiz) {
    var currentQuestionNumber = quiz.questionIndex + 1;
    var element = document.getElementById("progress");
    element.innerHTML = "Question " + currentQuestionNumber + " of " + quiz.questions.length;
};
 
function showScores(quiz) {
    var gameOverHTML = "<h1>Result</h1>";
    gameOverHTML += "<h2 id='score'> Your scores: " + quiz.score + "</h2>";
    var element = document.getElementById("quiz");
    element.innerHTML = gameOverHTML;
};
 
 
// create questions here
var currQuestions = [];
function loadQuestions()
{

    fetch('questions.json')
      .then((response) => {
        return response.text();
      })
      .then((dataStr) => {
            //Get each of the inputs by id
            let data = JSON.parse(dataStr);
            var module = data.module.name;
            data.module.questions.forEach(function(question, index)
            {
                var correctInput = question.correct_answer;
                //pass the values of the inputs into the addQuestion method in the quiz object which will add them to question array
                q = new Question(module, question.question, question.answers, question.answers[question.correct_answer - 1]);
                currQuestions.push(q);
                var quiz = new Quiz(currQuestions);
                 
                // display quiz
                populate(quiz);
            });
      });
}

function Team(teamData, org) {
    this.org = org;
    this.members = 0;
    this.number = teamData.number;
    this.name = teamData.name;
}
 
var currTeams = [];

// Check if all teams finished scoring
function checkTeamSCore()
{
    currTeams.forEach(function(team, index)
    {
        id = "team-id-"+team.name;
        if (teamScores[id] === -1)
            return false;
    });
    return true;
}

// Retrieve data from server and populate
function updateTeamLoad(teams)
{
    fetch(server_addr_request_scores)
      .then((response) => {
        return response.text();
      })
      .then((dataStr) => {
            //Get each of the inputs by id
            console.log(dataStr);
            let key_status = JSON.parse(dataStr);
            var responseElem = document.getElementById("teamResponses");
            if (null === responseElem)
            {
                clearInterval(periodicUpdateTeamLoadID);
                return;
            }
            responseElem.textContent = "Waiting for teams..."
            for(var station_id in key_status) 
            {
                var choice = key_status[station_id];
                // Check if it exists
                var teamLi = document.getElementById("teamResponse-id-"+station_id);
                if (null === teamLi)
                {
                    teamLi = document.createElement("li");
                    teamLi.id = "teamResponse-id-"+station_id; // Has to be same as earlier
                    responseElem.appendChild(teamLi);
                }
                teamLi.textContent = "Team [" + station_id + "] selected [" + choice + "]";
            }
      });
}
var periodicUpdateTeamLoadID;
function loadTeams()
{
    fetch('teams.json')
      .then((response) => {
        return response.text();
      })
      .then((dataStr) => {
            //Get each of the inputs by id
            let data = JSON.parse(dataStr);
            var org = data.org;
            data.teams.forEach(function(team, index)
            {
                tm = new Team(team, org);
                currTeams.push(tm);
            });
            // Start requesting the team status
            periodicUpdateTeamLoadID = setInterval(function(){updateTeamLoad(currTeams);}, 1000);
      });
}

function loadConfig()
{
    fetch('config.json')
    .then((response) => {
        return response.text();
    })
    .then((dataStr) => {
        let data = JSON.parse(dataStr);
        server_addr_request_scores = "http://" + data.server + ":" + data.port + "/request_station_status"
        server_addr_reset_scores = "http://" + data.server + ":" + data.port + "/reset_station_status"
        // create quiz
        loadQuestions();
        //  load teams
        loadTeams();
    });
}

// Configure first
loadConfig();
