<!doctype html>
<!--[if lte IE 7]> <html class="no-js ie67 ie678" lang="fr"> <![endif]-->
<!--[if IE 8]> <html class="no-js ie8 ie678" lang="fr"> <![endif]-->
<!--[if IE 9]> <html class="no-js ie9" lang="fr"> <![endif]-->
<!--[if gt IE 9]> <!--><html class="no-js" lang="fr"> <!--<![endif]-->
<head>
		<meta charset="UTF-8">
		<!--[if IE]><meta http-equiv="X-UA-Compatible" content="IE=edge"><![endif]-->
		<title>PauLLa.FiSh</title>
		<meta name="viewport" content="initial-scale=1.0">
		<!--[if lt IE 9]>
		<script src="//html5shiv.googlecode.com/svn/trunk/html5.js"></script>
		<![endif]-->
		<link rel="stylesheet" href="${request.route_path('list')}static/css/knacss.css" media="all">
		<link rel="stylesheet" href="${request.route_path('list')}static/css/styles.css" media="all">
</head>
<body>
	
	<a class="header" href="${request.route_path('list')}">
	<header id="header" role="banner" class="line pam txtcenter">
		<h1>PauLLa.FiSh : File Sharing<h1>
	</header>
	</a>
	
	<div id="main" role="main" class="row">
		<div class="col w20 pam aside">
			<nav id="navigation" role="navigation">
				<ul class="pam">
<a href="${request.route_path('new')}">Add a new file</a>
	    		</ul>
    		</nav>
			</div>
		<div class="col pam content">

% if request.session.peek_flash():
<p class="flash">
<% flash = request.session.pop_flash() %>
% for message in flash:
${message}<br>
% endfor
</p>
% endif
<ul class="pam test">
${next.body()}
</ul>
		</div>
		</div>
	
	<footer id="footer" role="contentinfo" class="line pam txtcenter">
		<a class='footer' href="http://www.paulla.asso.fr/">Site de l'association "PauLLa"</a></br>
    	<a class='footer' href="https://github.com/paulla/paulla.fish">Code sur Github.com</a>
	</footer>
	

</body>
</html>
