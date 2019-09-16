# -*- coding: utf-8 -*-

import datetime
import logging
import markdown
import textwrap

from flask import (
    render_template,
    flash,
    url_for,
    redirect,
    request,
    session,
    abort,
)
from flask_login import current_user

from sqlalchemy import desc

from app import db
from app.decorators import login_required
from app.models import Annotation, Dataset, Task
from app.main import bp
from app.main.forms import NextForm
from app.main.routes import RUBRIC
from app.utils.datasets import load_data_for_chart, get_demo_true_cps

LOGGER = logging.getLogger(__name__)

# textwrap.dedent is used mostly for code formatting.
DEMO_DATA = {
    1: {
        "dataset": {"name": "demo_100"},
        "learn": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                Welcome to AnnotateChange, an annotation app for change point 
                detection.

                Our goal with AnnotateChange is to create a dataset of 
                human-annotated time series to use in the development and 
                evaluation of change point algorithms.

                We really appreciate that you've agreed to help us with this! 
                Without your help this project would not be possible.

                In the next few pages, we'll introduce you to the problem of 
                change point detection. We'll look at a few datasets and see 
                different types of changes that can occur.

                Thanks again for your help!"""
                )
            )
        },
        "annotate": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                Please mark the point(s) in the time series where an **abrupt 
                change** in the behaviour of the series occurs.  The goal is to 
                define segments of the time series that are separated by places 
                where these abrupt changes occur. You can mark a point by 
                clicking on it. A marked point can be unmarked by clicking on 
                it again.

                Click "Submit" when you have finished marking the change points 
                or "No change points" when you believe there are none. You can 
                reset the graph with the "Reset" button.

                """
                )
            )
        },
        "evaluate": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                This first example has **one** change point. Not all datasets 
                that you'll encounter in this program have exactly one change 
                point. It is up to you to see whether a time series contains a 
                change point or not, and if it does, to see if there is more 
                than one.

                Don't worry if you weren't exactly correct on the first try. 
                The goal of this introduction is to familiarise yourself with 
                time series data and with change point detection in particular. 

                Note that in general we consider the change point to be the 
                point where the new behaviour *starts*, not the last point of 
                the current behaviour."""
                )
            )
        },
    },
    2: {
        "dataset": {"name": "demo_200"},
        "learn": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                In the previous example, you've seen a relatively simple 
                dataset where a *step change* occurred at a certain point in 
                time. A step change is one of the simplest types of change 
                points that can occur.

                Click "Continue" to move on to the next example."""
                )
            )
        },
        "annotate": {"text": RUBRIC},
        "evaluate": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                The dataset in the previous example shows again a time series 
                with step changes, but here there are **two** change points. 
                This is important to keep in mind, as there can be more than 
                one change point in a dataset."""
                )
            )
        },
    },
    3: {
        "dataset": {"name": "demo_300"},
        "learn": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                    In the previous examples we've introduced *step changes*. 
                    However, these are not the only types of change points that 
                    can occur, as we'll see in the next example."""
                )
            )
        },
        "annotate": {"text": RUBRIC},
        "evaluate": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                This time series shows an example where a change occurs in the 
                **variance** of the data. At the change point the variance of 
                the noise changes abruptly from a relatively low noise variance 
                to a high noise variance. This is another type of change point 
                that can occur."""
                )
            )
        },
    },
    4: {
        "dataset": {"name": "demo_400"},
        "learn": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                So far we have seen two types of change points: step changes 
                (also known as mean shift) and variance changes."""
                )
            )
        },
        "annotate": {"text": RUBRIC},
        "evaluate": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                Remember that it's also possible for there to be *no change 
                points* in a dataset. It can sometimes be difficult to tell 
                whether a dataset has change points or not. In that case, it's 
                important to remember that we are looking for points where the 
                behaviour of the time series changes *abruptly*."""
                )
            )
        },
    },
    5: {
        "dataset": {"name": "demo_500"},
        "learn": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                Change points mark places in the time series where the 
                behaviour changes *abruptly*. While **outliers** are data 
                points that do not adhere to the prevailing behaviour of the 
                time series, they are not generally considered change points 
                because the behaviour of the time series before and after the 
                outlier is the same. """
                )
            )
        },
        "annotate": {"text": RUBRIC},
        "evaluate": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                Outliers are quite common in real-world time series data, and 
                not all change point detection methods are robust against these 
                observations.

                Note that short periods that consist of several consecutive 
                outlying data points could be considered an abrupt change in 
                behaviour of the time series. If you see this, use your 
                intuition to guide you."""
                )
            )
        },
    },
    6: {
        "dataset": {"name": "demo_600"},
        "learn": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                So far we've seen *step changes*, *variance changes*, and time 
                series with *outliers*. Can you think of another type of change 
                that can occur?"""
                )
            )
        },
        "annotate": {"text": RUBRIC},
        "evaluate": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                What we see here is a change in *trend*. Changes in trend are 
                not always change points: gradual changes in direction are 
                common and should not be considered to be *abrupt* changes. 

                For trend changes it's not always easy to figure out exactly 
                where the change occurs, so it's harder to get it exactly 
                right. Use your intuition and keep in mind that it is normal 
                for the observations to be noisy."""
                )
            )
        },
    },
    7: {
        "dataset": {"name": "demo_650"},
        "learn": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                The datasets we've seen so far are all relatively well behaved, 
                but real-world time series are often more chaotic.
                """
                )
            )
        },
        "annotate": {"text": RUBRIC},
        "evaluate": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                This was an example of a <a 
                href="https://en.wikipedia.org/wiki/Random_walk" 
                target="_blank">random walk</a> without a change point. Some 
                time series data will look similar to this random walk, in the 
                sense that it varies over time and changes, but doesn't 
                actually ever change **abruptly**.  This is important to keep 
                in mind, because not all datasets that you'll see will 
                necessarily have change points (it's up to you to decide!)
                """
                )
            )
        },
    },
    8: {
        "dataset": {"name": "demo_700"},
        "learn": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                It is not uncommon for time series data from the real world to 
                display **seasonal variation**, for instance because certain 
                days of the week are more busy than others. Seasonality can 
                make it harder to find the change points in the dataset (if 
                there are any at all). Try to follow the pattern of 
                seasonality, and check whether the pattern changes in its 
                behaviour or in one of the ways that we've seen previously."""
                )
            )
        },
        "annotate": {"text": RUBRIC},
        "evaluate": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                As you can see from this example, changes in the periodicity of 
                the seasonal effect can occur as well. We expect that these 
                kinds of changes are quite rare, but it's nevertheless good to 
                be aware of them. 

                It is also important to note that seasonal effects on their own 
                do not constitute change points. For instance, a shift from the 
                winter season to the summer will show a change in passenger 
                numbers at the airport, but this will generally not be an 
                *abrupt* change.

                In some cases, it can help to *blur your eyes* to get a more 
                "global" view of the time series.
                """
                )
            )
        },
    },
    9: {
        "dataset": {"name": "demo_800"},
        "learn": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                    In practice time series datasets are not just one 
                    dimensional, but can be multidimensional too. A change 
                    point in such a time series does not necessarily occur in 
                    all dimensions simultaneously. It is therefore important to 
                    evaluate the behaviour of each dimension individually, as 
                    well as in relation to each other."""
                )
            )
        },
        "annotate": {"text": RUBRIC},
        "evaluate": {
            "text": markdown.markdown(
                textwrap.dedent(
                    """
                        In this example of a multidimensional time series, the 
                        change only occurred in a single dimension."""
                )
            )
        },
    },
}


def demo_performance(user_id):
    score = 0
    for demo_id in DEMO_DATA:
        dataset = Dataset.query.filter_by(
            name=DEMO_DATA[demo_id]["dataset"]["name"]
        ).first()
        tasks = (
            Task.query.filter_by(annotator_id=user_id, dataset_id=dataset.id)
            .order_by(desc(Task.annotated_on))
            .limit(1)
            .all()
        )
        task = tasks[0]
        annotations = (
            Annotation.query.join(Task, Annotation.task)
            .filter_by(id=task.id)
            .all()
        )

        true_cp = get_demo_true_cps(dataset.name)
        user_cp = [a.cp_index for a in annotations if not a.cp_index is None]
        if len(true_cp) == len(user_cp) == 0:
            score += 1
            continue

        n_correct, n_window, n_fp, n_fn = metrics(true_cp, user_cp)
        n_tp = n_correct + n_window
        f1 = (2 * n_tp) / (2 * n_tp + n_fp + n_fn)

        score += f1
    score /= len(DEMO_DATA)
    return score


def redirect_user(demo_id, phase_id):
    last_demo_id = max(DEMO_DATA.keys())
    demo_last_phase_id = 3
    if demo_id == last_demo_id and phase_id == demo_last_phase_id:
        # User is already introduced (happens if they redo the demo)
        if current_user.is_introduced:
            return redirect(url_for("main.index"))

        # check user performance
        if demo_performance(current_user.id) < 0.75:
            flash(
                "Unfortunately your performance on the introduction "
                "datasets was not as high as we would like. Please go "
                "through the introduction one more time to make sure "
                "that you understand and are comfortable with change "
                "point detection."
            )
            return redirect(url_for("main.index"))
        else:
            flash("Thank you for completing the introduction!", "success")

        # mark user as introduced
        current_user.is_introduced = True
        db.session.commit()

        return redirect(url_for("main.index"))
    elif phase_id == demo_last_phase_id:
        demo_id += 1
        phase_id = 1
        return redirect(
            url_for("main.demo", demo_id=demo_id, phase_id=phase_id)
        )
    else:
        phase_id += 1
        return redirect(
            url_for("main.demo", demo_id=demo_id, phase_id=phase_id)
        )


def process_annotations(demo_id):
    annotation = request.get_json()
    if annotation["identifier"] != demo_id:
        LOGGER.error(
            "User %s returned a task id in the demo that wasn't the demo id."
            % current_user.username
        )
        flash(
            "An internal error occurred, the administrator has been notified.",
            "error",
        )
        return redirect(url_for("main.index"))

    retval = []
    if not annotation["changepoints"] is None:
        retval = [int(cp["x"]) for cp in annotation["changepoints"]]

    # If the user is already introduced, we assume that their demo annotations
    # are already in the database, and thus we don't put them back in (because
    # we want the original ones).
    if current_user.is_introduced:
        return retval

    dataset = Dataset.query.filter_by(
        name=DEMO_DATA[demo_id]["dataset"]["name"]
    ).first()

    # Create a new task
    task = Task(annotator_id=current_user.id, dataset_id=dataset.id)
    task.done = False
    task.annotated_on = None
    db.session.add(task)
    db.session.commit()
    if annotation["changepoints"] is None:
        ann = Annotation(cp_index=None, task_id=task.id)
        db.session.add(ann)
        db.session.commit()
    else:
        for cp in annotation["changepoints"]:
            ann = Annotation(cp_index=cp["x"], task_id=task.id)
            db.session.add(ann)
            db.session.commit()

    # mark task as done
    task.done = True
    task.annotated_on = datetime.datetime.utcnow()
    db.session.commit()

    return retval


def metrics(true_cp, user_cp, k=5):
    true_cp = [int(x) for x in true_cp]
    user_cp = [int(x) for x in user_cp]

    correct = []
    window = []
    incorrect = []
    rem_true = list(true_cp)

    for cp in user_cp:
        if cp in rem_true:
            correct.append(cp)
            rem_true.remove(cp)
    user_cp = [x for x in user_cp if not x in correct]

    for cp in user_cp:
        to_delete = []
        for y in rem_true:
            if abs(cp - y) < k:
                window.append(cp)
                to_delete.append(y)
                break
        for y in to_delete:
            rem_true.remove(y)
    user_cp = [x for x in user_cp if not x in window]

    for cp in user_cp:
        incorrect.append(cp)

    n_correct = len(correct)
    n_window = len(window)
    n_fp = len(incorrect)
    n_fn = len(rem_true)
    return n_correct, n_window, n_fp, n_fn


def get_user_feedback(true_cp, user_cp):
    """Generate HTML to show as feedback to the user"""
    n_correct, n_window, n_fp, n_fn = metrics(true_cp, user_cp)

    text = "\n\n*Feedback:*\n\n"
    if len(true_cp) == len(user_cp) == 0:
        text += " - *Correctly identified that there are no change points.*\n"
    if len(true_cp) > 0:
        text += f"- *Number of changepoints exactly correct: {n_correct}.*\n"
    if n_window:
        text += f"- *Number of points correct within a 5-step window: {n_window}.*\n"
    if n_fp:
        text += f"- *Number of incorrectly identified points: {n_fp}.*\n"
    if n_fn:
        text += f"- *Number of missed change points: {n_fn}.*"
    text.rstrip()

    text = markdown.markdown(text)
    return text


def demo_learn(demo_id, form):
    demo_data = DEMO_DATA[demo_id]["learn"]
    return render_template(
        "demo/learn.html",
        title="Introduction – %i" % demo_id,
        text=demo_data["text"],
        form=form,
    )


def demo_annotate(demo_id):
    demo_data = DEMO_DATA[demo_id]["annotate"]
    dataset = Dataset.query.filter_by(
        name=DEMO_DATA[demo_id]["dataset"]["name"]
    ).first()
    if dataset is None:
        LOGGER.error(
            "Demo requested unavailable dataset: %s"
            % DEMO_DATA[demo_id]["dataset"]["name"]
        )
        flash(
            "An internal error occured. The administrator has been notified. We apologise for the inconvenience, please try again later.",
            "error",
        )
        return redirect(url_for("main.index"))

    chart_data = load_data_for_chart(dataset.name, dataset.md5sum)
    is_multi = len(chart_data["chart_data"]["values"]) > 1
    return render_template(
        "annotate/index.html",
        title="Introduction – %i" % demo_id,
        data=chart_data,
        rubric=demo_data["text"],
        identifier=demo_id,
        is_multi=is_multi,
    )


def demo_evaluate(demo_id, phase_id, form):
    demo_data = DEMO_DATA[demo_id]["evaluate"]
    user_changepoints = session.get("user_changepoints", "__UNK__")
    if user_changepoints == "__UNK__":
        flash(
            "The previous step of the demo was not completed successfully. Please try again.",
            "error",
        )
        return redirect(
            url_for("main.demo", demo_id=demo_id, phase_id=phase_id - 1)
        )
    dataset = Dataset.query.filter_by(
        name=DEMO_DATA[demo_id]["dataset"]["name"]
    ).first()
    chart_data = load_data_for_chart(dataset.name, dataset.md5sum)
    is_multi = len(chart_data["chart_data"]["values"]) > 1
    true_changepoints = get_demo_true_cps(dataset.name)
    if true_changepoints is None:
        flash(
            "An internal error occurred, the administrator has been notified. We apologise for the inconvenience, please try again later.",
            "error",
        )
        return redirect(url_for("main.index"))

    feedback = get_user_feedback(true_changepoints, user_changepoints)

    annotations_true = [dict(index=x) for x in true_changepoints]
    annotations_user = [dict(index=x) for x in user_changepoints]
    return render_template(
        "demo/evaluate.html",
        title="Introduction – %i" % demo_id,
        data=chart_data,
        annotations_user=annotations_user,
        annotations_true=annotations_true,
        text=demo_data["text"],
        feedback=feedback,
        form=form,
        is_multi=is_multi,
    )


@bp.route(
    "/introduction/",
    defaults={"demo_id": 1, "phase_id": 1},
    methods=("GET", "POST"),
)
@bp.route(
    "/introduction/<int:demo_id>/",
    defaults={"phase_id": 1},
    methods=("GET", "POST"),
)
@bp.route(
    "/introduction/<int:demo_id>/<int:phase_id>", methods=("GET", "POST")
)
@login_required
def demo(demo_id, phase_id):
    form = NextForm()

    if request.method == "POST":
        if form.validate_on_submit():
            return redirect_user(demo_id, phase_id)
        else:
            user_changepoints = process_annotations(demo_id)
            session["user_changepoints"] = user_changepoints
            return url_for("main.demo", demo_id=demo_id, phase_id=phase_id + 1)

    if phase_id == 1:
        return demo_learn(demo_id, form)
    elif phase_id == 2:
        return demo_annotate(demo_id)
    elif phase_id == 3:
        return demo_evaluate(demo_id, phase_id, form)
    else:
        abort(404)
